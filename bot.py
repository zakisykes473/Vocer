import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random, time, requests

# === KONFIGURASI ===
TELEGRAM_TOKEN = "7654295973:AAGVfUSyKqgmrzqmUn3CwgF8Qq3yFxAg-bE"
TELEGRAM_CHAT_ID = "6312801995"
TARGET_URL = "https://www.joinmarriottbonvoy.com/gojek/s/EN-GB/"
EMAIL_FILE = "file.txt"

# Lokasi Chromium untuk Termux (sesuaikan jika beda)
CHROMIUM_PATH = "/data/data/com.termux/files/usr/bin/chromium"

# === Fungsi kirim notifikasi ke Telegram ===
def kirim_telegram(pesan):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": pesan},
        )
    except Exception as e:
        print(f"Gagal kirim ke Telegram: {e}")

# === Generate nama random ===
def generate_nama():
    depan = ["Zaki", "Fajar", "Rizal", "Dina", "Putri", "Sari", "Budi", "Rina", "Agus"]
    belakang = ["Sykes", "Wijaya", "Rahma", "Saputra", "Utami", "Permadi"]
    return random.choice(depan) + " " + random.choice(belakang)

# === Proses 1 email ===
def proses_email(email):
    print(f"\n=== Mulai proses email: {email} ===")
    kirim_telegram(f"Mulai klaim voucher untuk: {email}")

    options = uc.ChromeOptions()
    options.binary_location = CHROMIUM_PATH
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = uc.Chrome(options=options)
        driver.get(TARGET_URL)

        # Tunggu form muncul (maks 20 detik)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "firstName")))

        # Isi nama dan email
        driver.find_element(By.NAME, "firstName").send_keys(generate_nama())
        driver.find_element(By.NAME, "lastName").send_keys("AutoBot")
        driver.find_element(By.NAME, "email").send_keys(email)

        # Ceklis checkbox
        checkbox = driver.find_element(By.NAME, "checkBoxForm")
        if not checkbox.is_selected():
            checkbox.click()

        # Submit
        submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()

        time.sleep(5)  # Tunggu proses

        kirim_telegram(f"Sukses submit: {email}")
        print(f"✅ Sukses klaim: {email}")
        driver.quit()
    except Exception as e:
        kirim_telegram(f"❌ Gagal proses {email}: {str(e)}")
        print(f"❌ Error dengan {email}: {e}")
        driver.quit()
        time.sleep(3)
        proses_email(email)  # Retry tanpa batas

# === Main ===
with open(EMAIL_FILE, "r") as f:
    daftar_email = [x.strip() for x in f.readlines() if x.strip()]

for email in daftar_email:
    proses_email(email)
