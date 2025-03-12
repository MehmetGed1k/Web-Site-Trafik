import os
import random
import asyncio
import requests
from playwright.async_api import async_playwright

# Proxy ve site dosyalarının yolları
OUTPUT_DIR = r"C:\\Users\\alone\\Desktop\\proxler"
sites_file = os.path.join(OUTPUT_DIR, "sites.txt")
proxies_file = os.path.join(OUTPUT_DIR, "sock5.txt")

# Proxy kullanıcı adı ve şifre
PROXY_USERNAME = "USFXUJ6OI"
PROXY_PASSWORD = "PF132wz6"

# Kullanıcı ajanları (User-Agent)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
]

# Fake donanım bilgileri
CPU_MODELS = ["Intel Core i9-13900K", "Intel Core i7-13700K", "AMD Ryzen 9 7950X"]
GPU_MODELS = ["NVIDIA GeForce RTX 4090", "AMD Radeon RX 7900 XTX"]
RAM_SIZES = [8, 16, 32, 64]
OS_PLATFORMS = ["Win32", "Win64", "MacIntel", "Linux x86_64"]

# Dosyadan veri okuma fonksiyonu
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

# Proxy ile siteyi ziyaret etme fonksiyonu
async def visit_sites_with_proxies():
    while True:
        proxies = read_file(proxies_file)
        sites = read_file(sites_file)

        async with async_playwright() as p:
            for proxy in proxies:
                proxy_ip, proxy_port = proxy.split(":")
                proxy_url = f"socks5://{PROXY_USERNAME}:{PROXY_PASSWORD}@{proxy_ip}:{proxy_port}"
                print(f"\n🔄 Yeni proxy kullanılıyor: {proxy_url}")

                user_agent = random.choice(USER_AGENTS)
                fake_cpu = random.choice(CPU_MODELS)
                fake_gpu = random.choice(GPU_MODELS)
                fake_ram = random.choice(RAM_SIZES)
                fake_os = random.choice(OS_PLATFORMS)

                try:
                    # Tarayıcı başlatma
                    browser = await p.chromium.launch(
                        headless=False,
                        proxy={"server": proxy_url},
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--no-sandbox",
                            "--disable-setuid-sandbox"
                        ]
                    )
                    context = await browser.new_context(user_agent=user_agent)

                    # Fake donanım bilgilerini ekle
                    await context.add_init_script(f"""
                        Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {random.randint(2, 16)} }});
                        Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fake_ram} }});
                        Object.defineProperty(navigator, 'platform', {{ get: () => "{fake_os}" }});
                    """)

                    # Fake GPU bilgisi
                    await context.add_init_script(f"""
                        const getParameter = WebGLRenderingContext.prototype.getParameter;
                        WebGLRenderingContext.prototype.getParameter = function(param) {{
                            if (param === 37446) return "{fake_gpu}";
                            if (param === 37445) return "NVIDIA Corporation";
                            return getParameter.call(this, param);
                        }};
                    """)

                    page = await context.new_page()

                    # Proxy IP doğrulama
                    print("🔍 Proxy üzerinden IP doğrulanıyor...")
                    await page.goto("https://api.myip.com/")
                    ip_check = await page.content()
                    print(f"🌍 Proxy IP doğrulandı: {ip_check}")

                    for site in sites:
                        try:
                            print(f"🔗 Siteye bağlanılıyor: {site}")
                            await page.goto(site, timeout=10000)
                            await page.wait_for_load_state("load")

                            # Google giriş sayfası kontrolü
                            if "accounts.google.com" in page.url:
                                print("⚠ Google giriş sayfası tespit edildi, giriş yapılıyor...")

                                await page.fill('input[type="email"]', "seningmailexample@gmail.com")
                                await page.click('button:has-text("İleri")')
                                await asyncio.sleep(3)
                                await page.fill('input[type="password"]', "şifreniburada")
                                await page.click('button:has-text("İleri")')
                                await asyncio.sleep(5)

                            # İnsan davranışı simülasyonu
                            await asyncio.sleep(random.uniform(2, 5))
                            for _ in range(random.randint(2, 5)):
                                await page.mouse.wheel(0, random.randint(100, 500))
                                await asyncio.sleep(random.uniform(1, 3))

                            print(f"✅ {site} ziyaret edildi, 10 saniye bekleniyor...")
                            await asyncio.sleep(10)
                        except Exception as e:
                            print(f"❌ Hata: {e}")
                            break

                    await browser.close()
                except Exception as e:
                    print(f"⚠ Proxy bağlantı hatası: {e}")

        print("🔁 Tüm proxy'ler tamamlandı, baştan başlıyoruz...")

# Ana fonksiyonu çalıştır
asyncio.run(visit_sites_with_proxies())
