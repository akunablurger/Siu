import os
import time
from playwright.sync_api import sync_playwright

def run():
    # Menerima data 1 akun (format: email:password) dari matrix job
    account_str = os.getenv("CURRENT_ACCOUNT", "")
    # Menerima 5 URL target yang dipisahkan oleh tanda koma (,)
    targets_str = os.getenv("TARGET_URLS", "")

    if not account_str or ":" not in account_str:
        print("[ERROR] Akun tidak valid atau kosong!")
        return

    email, password = account_str.split(":", 1)
    email = email.strip()
    password = password.strip()

    # Ubah string URL berpisah koma menjadi list Python
    target_urls = [url.strip() for url in targets_str.split(",") if url.strip()]

    if not target_urls:
        print("[ERROR] Target URL kosong!")
        return

    print(f"\n================================")
    print(f"[PROSES] Memproses Akun: {email}")
    print(f"[INFO] Jumlah Target URL: {len(target_urls)}")
    print(f"================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--start-maximized"
            ]
        )

        # Buat context terisolasi untuk akun ini
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        
        # 1. Tab Login Gmail
        page_login = context.new_page()

        try:
            print(f"[{email}] Membuka halaman login Google...")
            page_login.goto("https://accounts.google.com/", timeout=60000)

            # Input Email
            print(f"[{email}] Mengisi email...")
            page_login.wait_for_selector('input[type="email"]', timeout=10000)
            page_login.fill('input[type="email"]', email)
            page_login.click('#identifierNext')

            # Input Password
            print(f"[{email}] Menunggu form password...")
            page_login.wait_for_selector('input[type="password"]', timeout=15000)
            time.sleep(2)
            
            print(f"[{email}] Mengisi password...")
            page_login.fill('input[type="password"]', password)
            page_login.click('#passwordNext')

            print(f"[{email}] Menunggu proses login selesai...")
            time.sleep(8) 

        except Exception as e:
            print(f"[{email}] Kendala saat login otomatis: {e}")

        # Tutup tab login
        page_login.close()

        # 2. Membuka 5 Tab untuk 5 URL AI Studio yang berbeda secara paralel
        for idx, url in enumerate(target_urls, start=1):
            new_page = context.new_page()
            try:
                print(f"[{email}] Membuka Tab {idx} -> {url}")
                new_page.goto(url, timeout=60000)
            except Exception as ex:
                print(f"[{email}] Gagal membuka tab {idx} ({url}): {ex}")
            time.sleep(1)

        print(f"[{email}] Semua tab berhasil di
