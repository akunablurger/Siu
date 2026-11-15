import os
import time
from playwright.sync_api import sync_playwright

def get_accounts_from_env():
    accounts = []
    # Format di GitHub Secret nantinya: email1:pass1 (baris baru) email2:pass2
    raw_data = os.getenv("ACCOUNTS_DATA", "")
    
    for line in raw_data.strip().split("\n"):
        line = line.strip()
        if line and ":" in line:
            email, password = line.split(":", 1)
            accounts.append({"email": email.strip(), "password": password.strip()})
            
    print(f"[INFO] Berhasil memuat {len(accounts)} akun dari GitHub Secrets.")
    return accounts

def run():
    accounts = get_accounts_from_env()
    if not accounts:
        print("[ERROR] Tidak ada akun yang ditemukan di environment variable!")
        return

    with sync_playwright() as p:
        # Di GitHub Actions (CI), browser disarankan berjalan headless=False dengan Xvfb atau headless=True. 
        # Catatan: Login Google sering mendeteksi bot jika headless=True murni. 
        # Kita gunakan headless=False dengan tambahan argumen agar aman.
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

            # Buat context baru untuk isolasi cookies/sesi tiap akun
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
                time.sleep(8) # Jeda untuk sinkronisasi sesi

            except Exception as e:
                print(f"[{email}] Kendala saat login otomatis: {e}")

            # Tutup halaman login atau biarkan, lalu buka 5 tab AI Studio
            page_login.close()

            print(f"[{email}] Membuka 5 tab Google AI Studio...")
            tabs = []
