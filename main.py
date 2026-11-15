import os
import time
from playwright.sync_api import sync_playwright

def run():
    # Mengambil data dari 2 secret (berisi baris-baris teks dengan enter)
    accounts_raw = os.getenv("ACCOUNTS_SECRET", "")
    urls_raw = os.getenv("AI_STUDIO_URLS_SECRET", "")

    # Parsing akun (pisahkan berdasarkan baris / enter)
    accounts = []
    for line in accounts_raw.strip().split("\n"):
        line = line.strip()
        if line and ":" in line:
            email, password = line.split(":", 1)
            accounts.append({"email": email.strip(), "password": password.strip()})

    # Parsing URL (pisahkan berdasarkan baris / enter)
    target_urls = [url.strip() for url in urls_raw.strip().split("\n") if url.strip()]

    if not accounts:
        print("[ERROR] Tidak ada akun ditemukan di ACCOUNTS_SECRET!")
        return

    if not target_urls:
        print("[ERROR] Tidak ada URL ditemukan di AI_STUDIO_URLS_SECRET!")
        return

    print(f"[INFO] Total akun dimuat: {len(accounts)}")
    print(f"[INFO] Total URL target dimuat: {len(target_urls)}")

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

        # Melakukan looping untuk setiap akun secara berurutan/paralel
        for index, acc in enumerate(accounts, start=1):
            email = acc["email"]
            password = acc["password"]

            print(f"\n================================")
            print(f"[PROSES] Akun ke-{index}: {email}")
            print(f"================================")

            # Buat context terisolasi untuk tiap akun agar cookies tidak tercampur
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
