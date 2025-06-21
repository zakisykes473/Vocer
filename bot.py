import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import random
import requests

# === Telegram kamu ===
TELEGRAM_BOT_TOKEN = "7654295973:AAGVfUSyKqgmrzqmUn3CwgF8Qq3yFxAg-bE"
TELEGRAM_CHAT_ID = "6312801995"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, data=payload)
        if res.status_code == 200:
            print("📩 Notifikasi Telegram terkirim.")
        else:
            print("⚠️ Gagal kirim Telegram:", res.text)
    except Exception as e:
        print("❌ Error kirim Telegram:", e)

def generate_random_name():
    first_names = ["Andi", "Budi", "Citra", "Dewi", "Eka", "Fajar"]
    last_names = ["Santoso", "Wijaya", "Saputra", "Lestari", "Halim", "Putra"]
    return random.choice(first_names), random.choice(last_names)

def wait_until_page_ready(driver, wait_time=5, email=""):
    attempt = 0
    while True:
        attempt += 1
        try:
            driver.find_element(By.ID, "firstName")
            print(f"✅ Halaman siap setelah {attempt} percobaan")
            return True
        except NoSuchElementException:
            print(f"[{attempt}] Halaman belum siap, refresh ulang...")
            time.sleep(wait_time)
            driver.refresh()
            if attempt % 10 == 0:
                send_telegram_message(
                    f"⚠️ <b>Masih mencoba klaim voucher</b>\n📧 Email: <code>{email}</code>\n🔁 Sudah {attempt}x refresh, halaman belum siap."
                )

# Baca daftar email
with open("file.txt", "r") as f:
    emails = [line.strip() for line in f if line.strip()]

for email in emails:
    print(f"\n=== Mulai proses email: {email} ===")
    
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")  # Hapus jika ingin lihat browser
    
    driver = uc.Chrome(options=options)
    driver.get("https://www.joinmarriottbonvoy.com/gojek/s/EN-GB/")

    # Tunggu sampai halaman bisa diisi (tanpa batas)
    wait_until_page_ready(driver, email=email)

    try:
        fname, lname = generate_random_name()
        driver.find_element(By.ID, "firstName").send_keys(fname)
        driver.find_element(By.ID, "lastName").send_keys(lname)
        driver.find_element(By.ID, "email").send_keys(email)

        checkbox = driver.find_element(By.XPATH, '//label[contains(@for,"privacyPolicy")]')
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(1)

        submit = driver.find_element(By.XPATH, '//button[contains(text(),"Join Now")]')
        submit.click()

        time.sleep(3)  # Tunggu submit

        send_telegram_message(
            f"✅ <b>Voucher diklaim</b>\n📧 Email: <code>{email}</code>\n👤 Nama: <code>{fname} {lname}</code>"
        )
        print(f"Sukses submit: {email}")

    except Exception as e:
        print(f"❌ Gagal submit untuk {email}: {e}")
        send_telegram_message(
            f"❌ <b>Gagal submit voucher</b>\n📧 Email: <code>{email}</code>\n👤 Nama: <code>{fname} {lname}</code>\n💥 Error: <code>{str(e)}</code>"
        )

    driver.quit()
    time.sleep(5)  # jeda antar email
