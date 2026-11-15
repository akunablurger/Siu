# Auto Login Gmail & Multi-Tab Google AI Studio

Repositori ini berisi skrip otomatisasi berbasis **Python & Playwright** untuk melakukan login otomatis ke akun Gmail (mendukung banyak akun) dan secara otomatis membukakan banyak tab sekaligus langsung menuju halaman **Google AI Studio (`aistudio.google.com`)**. Skrip ini juga diintegrasikan dengan **GitHub Actions** agar bisa berjalan secara otomatis di awan.

---

## 🚀 Fitur Utama
- **Multi-Account Support:** Mendukung banyak akun Gmail sekaligus yang dikelola dari file konfigurasi atau GitHub Secrets.
- **Multi-Tab Automation:** Setiap akun otomatis membukakan 5 tab sekaligus langsung ke dashboard AI Studio.
- **Anti-Bot Signatures:** Menggunakan argumen khusus untuk menyamarkan browser otomatis agar meminimalisir deteksi bot dari Google.
- **CI/CD Ready:** Dijalankan otomatis menggunakan GitHub Actions workflows.

---

## 📁 Struktur Repositori
```text
auto-login-aistudio/
├── .github/
│   └── workflows/
│       └── run-aistudio.yml
├── main.py
├── requirements.txt
└── README.md
