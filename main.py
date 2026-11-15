import os
import time
from playwright.sync_api import sync_playwright

def get_accounts_from_env():
    accounts = []
    raw_data = os.getenv("ACCOUNTS_DATA", "")
    for line in raw_data.strip().split("\n"):
        line = line.strip()
        if line and ":" in line:
            email, password = line.split(":", 1)
            accounts.append({"email": email.strip(), "password": password.strip()})
    return accounts

def run():
    accounts = get_accounts_from_env()
    target_url = os.getenv("TARGET_URL", "https://aistudio.google.com/") # Ambil dari secret, ada fallback default-nya

    if not accounts:
        print("[ERROR] Tidak ada akun ditemukan di ACCOUNTS_DATA!")
        return

    print(f"[INFO] Memuat {len(accounts)} akun. Target URL: {target_url}")

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

        for index, acc in enumerate(accounts, start=1):
            email = acc["email"]
            password = acc["password"]
            
            print(f"\n================================")
            print(f"[PROSES] Akun ke-{index}: {email}")
            print(f"================================")

            # Buat context terisolasi per akun
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            
            # Tab 1: Untuk proses Login Gmail
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

            # Membuka 5 tab sekaligus mengarah ke TARGET_URL dari secret
            print(f"[{email}] Membuka 5 tab menuju {target_url}...")
            for i in range(1, 6):
                new_page = context.new_page()
                try:
                    new_page.goto(target_url, timeout=60000)
                    print(f"[{email}] -> Tab {i} berhasil dibuka.")
                except Exception as ex:
                    print(f"[{email}] -> Gagal membuka tab {i}: {ex}")
                time.sleep(1)

            print(f"[{](streamdown:incomplete-link)
