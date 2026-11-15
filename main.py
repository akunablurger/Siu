import os
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def _env_bool(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _target_urls(raw: str) -> list[str]:
    urls = []
    for line in raw.splitlines():
        url = line.strip()
        parsed = urlparse(url)
        if not url:
            continue
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"URL target tidak valid: {url}")
        urls.append(url)
    return urls


def run() -> None:
    account_str = os.getenv("CURRENT_ACCOUNT", "").strip()
    urls_raw = os.getenv("AI_STUDIO_URLS_SECRET", "")

    if not account_str or ":" not in account_str:
        raise ValueError("CURRENT_ACCOUNT harus berformat email:password")

    email, password = account_str.split(":", 1)
    email = email.strip()
    password = password.strip()
    if not email or not password:
        raise ValueError("Email atau password kosong")

    target_urls = _target_urls(urls_raw)
    if not target_urls:
        raise ValueError("AI_STUDIO_URLS_SECRET tidak berisi URL")

    headless = _env_bool("HEADLESS", default=True)
    print(f"[INFO] Memproses akun: {email}")
    print(f"[INFO] Total URL target: {len(target_urls)}")
    print(f"[INFO] Playwright headless: {headless}")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        try:
            login_page = context.new_page()
            try:
                print(f"[{email}] Membuka halaman login Google...")
                login_page.goto("https://accounts.google.com/", wait_until="domcontentloaded", timeout=60000)
                login_page.locator('input[type="email"]').wait_for(timeout=15000)
                login_page.locator('input[type="email"]').fill(email)
                login_page.locator("#identifierNext").click()
                login_page.locator('input[type="password"]').wait_for(timeout=15000)
                login_page.locator('input[type="password"]').fill(password)
                login_page.locator("#passwordNext").click()
                login_page.wait_for_timeout(8000)

                if "challenge" in login_page.url or "signin" in login_page.url:
                    raise RuntimeError(
                        "Login Google belum selesai; kemungkinan 2FA, CAPTCHA, atau security challenge."
                    )
                print(f"[{email}] Login selesai: {login_page.url}")
            finally:
                login_page.close()

            for index, url in enumerate(target_urls, start=1):
                page = context.new_page()
                try:
                    print(f"[{email}] Membuka tab {index}/{len(target_urls)} -> {url}")
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                finally:
                    # Tab dibiarkan terbuka sampai proses selesai pada mode interaktif.
                    # Pada CI, tutup tab setelah navigasi agar job tidak menggantung.
                    if headless:
                        page.close()

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    run()
