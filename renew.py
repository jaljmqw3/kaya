import os
import time
from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("KATABUMP_EMAIL")
PASSWORD = os.environ.get("KATABUMP_PASSWORD")
SERVER_ID = os.environ.get("SERVER_ID", "d1712508")

def main():
    if not EMAIL or not PASSWORD:
        print("❌ خطا: متغیرهای KATABUMP_EMAIL یا KATABUMP_PASSWORD تعریف نشده‌اند.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()

        try:
            # ─── لاگین ───
            print("🔄 در حال ورود به Katabump...")
            page.goto("https://control.katabump.com/auth/login", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            user_input = page.locator('input[name="username"], input[name="email"], input[type="text"], input[type="email"]').first
            pass_input = page.locator('input[name="password"], input[type="password"]').first

            user_input.fill(EMAIL)
            pass_input.fill(PASSWORD)

            submit_btn = page.locator('button[type="submit"], input[type="submit"]').first
            submit_btn.click()
            page.wait_for_timeout(8000)

            print(f"🌐 رفتن به صفحه سرور {SERVER_ID}...")
            page.goto(f"https://control.katabump.com/server/{SERVER_ID}", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            # ─── پیدا کردن و کلیک دکمه Renew ───
            renew_selectors = [
                'button:has-text("Renew")',
                'a:has-text("Renew")',
                'button:has-text("renew")',
                'a:has-text("renew")',
                'button:has-text("تمدید")',
                'a:has-text("تمدید")',
            ]

            renew_btn = None
            for sel in renew_selectors:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        renew_btn = loc.first
                        print(f"✅ دکمه Renew پیدا شد (سلکتور: {sel})")
                        break
                except:
                    continue

            if renew_btn:
                renew_btn.click()
                print("🎉 دکمه Renew کلیک شد!")
                page.wait_for_timeout(5000)

                # اسکرین‌شات موفقیت
                page.screenshot(path="success_screenshot.png")
                print("📸 اسکرین‌شات موفقیت ذخیره شد.")
            else:
                print("ℹ️ دکمه Renew پیدا نشد. ممکنه سرور نیازی به تمدید نداره.")
                page.screenshot(path="no_renew_button.png")

        except Exception as e:
            print(f"❌ خطا: {e}")
            try:
                page.screenshot(path="error_screenshot.png")
                print("📸 اسکرین‌شات خطا ذخیره شد.")
            except:
                pass
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    main()
