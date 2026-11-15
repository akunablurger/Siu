import os
import time
from playwright.sync_api import sync_playwright

def run():
    # 1. Ambil data 1 akun dari matrix job GitHub Actions saat ini
    account_str = os.getenv("CURRENT_ACCOUNT", "")
    
    # 2. Ambil data URL target yang berisi baris-baris (enter ke bawah) dari secret
    urls_raw = os.getenv("AI_STUDIO_URLS_SECRET", "")

    if not account_str or ":" not in account_str:
        print("[ERROR] Akun matrix tidak valid atau kosong!")
        return

    email, password = account_str.split(":", 1)
    email = email.strip()
    password = password.strip()

    # Parsing URL (pisahkan berdasarkan baris / enter)
    target_urls = [url.strip() for url in urls_raw.strip().split("\n") if url.strip()]

    if not target_urls:
        print("[ERROR] Tidak ada URL ditemukan di AI_STUDIO_URLS_SECRET!")
        return

    print(f"\n================================")
    print(f"[PROSES MATRIX] Memproses Akun: {email}")
    print(f"[INFO] Total Target URL yang akan dibuka: {len(target_urls)}")
    print(f"================================")

    with sync_playwright() as p:
        # Jalankan browser (headless=False aman untuk debugging, di CI/CD github runner bisa berjalan)
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--start-maximized"
            ]
        )

        # Buat context terisolasi khusus untuk akun ini (cookies aman tidak tercampur)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        
        # Buka tab pertama untuk proses login Gmail
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
            time.sleep(2) # Jeda stabilisasi animasi
            
            print(f"[{email}] Mengisi password...")
            page_login.fill('input[type="password"]', password)
            page_login.click('#passwordNext')

            print(f"[{email}] Menunggu proses login selesai...")
            time.sleep(8) # Jeda sinkronisasi akun

        except Exception as e:
            print(f"[{email}] Kendala saat login otomatis: {e}")
            print(f"[{email}] Melanjutkan proses buka tab target...")

        # Tutup tab login agar bersih
        try:
            page_login.close()
        except:
            pass

        # Membuka semua URL target (berdasarkan baris secret) ke tab-tab baru secara berurutan
        for idx, url in enumerate(target_urls, start=1):
            new_page = context.new_page()
            try:
                print(f"[{email}] Membuka Tab {idx} -> {url}")
                new_page.goto(url, timeout=60000)
            except Exception as ex:
                print(f"[{email}] Gagal membuka tab {idx} ({url}): {ex}")
            time.
