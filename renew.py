import os
import time
from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("KATABUMP_EMAIL")
PASSWORD = os.environ.get("KATABUMP_PASSWORD")
SERVER_ID = os.environ.get("SERVER_ID", "388169")

BASE_URL = "https://dashboard.katabump.com"

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
            page.goto(f"{BASE_URL}/auth/login", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)

            # فرم لاگین Pterodactyl: فیلد "Your ID" (ایمیل) + "Password"
            user_selectors = [
                'input[name="username"]',
                'input[name="email"]',
                'input[type="email"]',
                'input[name="id"]',
                'input[placeholder*="ID"]',
                'input[placeholder*="Email"]',
                'input[placeholder*="email"]',
                'input[type="text"]',
            ]

            pass_selectors = [
                'input[name="password"]',
                'input[type="password"]',
            ]

            user_input = None
            for sel in user_selectors:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        user_input = loc.first
                        print(f"✅ فیلد کاربر پیدا شد (سلکتور: {sel})")
                        break
                except:
                    continue

            pass_input = None
            for sel in pass_selectors:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        pass_input = loc.first
                        print(f"✅ فیلد رمز پیدا شد (سلکتور: {sel})")
                        break
                except:
                    continue

            if not user_input or not pass_input:
                print("❌ فیلدهای لاگین پیدا نشدند!")
                page.screenshot(path="error_login_form.png")
                return

            user_input.fill(EMAIL)
            pass_input.fill(PASSWORD)

            # کلیک دکمه لاگین
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("ورود")',
            ]
            for sel in submit_selectors:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        loc.first.click()
                        print(f"✅ دکمه لاگین کلیک شد (سلکتور: {sel})")
                        break
                except:
                    continue

            page.wait_for_timeout(8000)
            print(f"📍 URL بعد از لاگین: {page.url}")
            page.screenshot(path="after_login.png")

            # ─── رفتن به صفحه سرور ───
            server_url = f"{BASE_URL}/servers/edit?id={SERVER_ID}"
            print(f"🌐 رفتن به صفحه سرور {SERVER_ID}...")
            page.goto(server_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            print(f"📍 URL صفحه سرور: {page.url}")
            page.screenshot(path="server_page.png")

            # ─── پیدا کردن و کلیک دکمه Renew ───
            renew_selectors = [
                'button:has-text("Renew")',
                'a:has-text("Renew")',
                'button:has-text("renew")',
                'a:has-text("renew")',
                'button:has-text("تمدید")',
                'a:has-text("تمدید")',
                'input[value*="Renew"]',
                'a[href*="renew"]',
                'button:has-text("Extend")',
                'button:has-text("extend")',
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
                page.screenshot(path="success_screenshot.png")
                print("📸 اسکرین‌شات موفقیت ذخیره شد.")

                # بررسی دیالوگ تأیید
                confirm_selectors = [
                    'button:has-text("Confirm")',
                    'button:has-text("OK")',
                    'button:has-text("Yes")',
                    'button:has-text("تایید")',
                ]
                for sel in confirm_selectors:
                    try:
                        loc = page.locator(sel)
                        if loc.count() > 0 and loc.first.is_visible():
                            loc.first.click()
                            print("✅ دکمه تأیید کلیک شد!")
                            page.wait_for_timeout(3000)
                            break
                    except:
                        continue

                page.screenshot(path="final_screenshot.png")
                print("🎉 تمدید با موفقیت انجام شد!")
            else:
                print("ℹ️ دکمه Renew پیدا نشد. ممکنه سرور نیازی به تمدید نداره.")
                body_text = page.locator("body").inner_text()
                print(f"📄 محتوای صفحه (۵۰۰ کاراکتر اول):\n{body_text[:500]}")

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
