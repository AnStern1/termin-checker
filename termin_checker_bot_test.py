import asyncio
import os
import requests
from playwright.async_api import async_playwright

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def check_termine():
    print("\U0001F310 Запускаем браузер...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("➡️ Переход на сайт...")
        await page.goto("https://terminvergabe.magdeburg.de")

        print("➡️ Шаг 1: Кликаем Ausländerbehörde")
        await page.get_by_text("Ausländerbehörde", exact=True).click()

        print("➡️ Шаг 2: Кликаем Aufenthaltstitel")
        await page.locator("h3:has-text('§16a, §16b, §16d, §16e, §16f')").click()

        print("➡️ Шаг 3: Кликаем кнопку + (Erhöhen)")
        await page.locator("button").nth(5).click()

        print("➡️ Шаг 4: Подтверждаем Hinweis")
        await page.locator("button:has-text('OK')").click()

        print("➡️ Шаг 5: Weiter на этапе выбора причины")
        await page.locator('input[type="submit"][value="Weiter"]').click()

        print("➡️ Шаг 6: Подтверждаем второй Hinweis")
        await page.locator("button:has-text('OK')").click()

        print("➡️ Шаг 7: Weiter на этапе Standort")
        await page.locator('input[type="submit"][value="Weiter"]').click()

        print("\U0001F52D Проверяем наличие свободных терминов...")
        content = await page.content()
        if "Kein freier Termin verfügbar" in content:
            print("❌ Свободных терминов нет.")
            if TELEGRAM_CHAT_ID and TELEGRAM_TOKEN:
                msg = "❌ Свободных терминов нет на сайте Ausländerbehörde Magdeburg."
                requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}")
        else:
            print("✅ Есть свободные термины!")
            if TELEGRAM_CHAT_ID and TELEGRAM_TOKEN:
                msg = "‼️ Есть свободные термины на сайте Ausländerbehörde Magdeburg!"
                requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}")

        await browser.close()

async def scheduler():
    while True:
        try:
            await check_termine()
        except Exception as e:
            print(f"⚠️ Ошибка при выполнении: {e}")
        print("⏳ Ожидаем 5 минут до следующей проверки...\n")
        await asyncio.sleep(300)  # 5 минут

if __name__ == "__main__":
    asyncio.run(scheduler())
