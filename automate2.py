from playwright.sync_api import sync_playwright

def flipkart_login(page):
    """Prompt user to fill Flipkart login and OTP."""
    try:
        # FIRST STEP → Phone number input
        phone_input = None

        # Detect phone field using Playwright label method
        try:
            phone_input = page.get_by_label("Enter Email/Mobile number")
        except:
            pass

        # Backup selectors
        if not phone_input or phone_input.count() == 0:
            selectors = [
                "input.c3Bd2c.XnemW5",
                "input[type='text']",
                "input[autocomplete='off']"
            ]
            for sel in selectors:
                locator = page.locator(sel)
                if locator.count() > 0:
                    phone_input = locator
                    break

        if phone_input and phone_input.count() > 0:
            phone_number = input("Enter your Flipkart phone number: ")
            phone_input.fill(phone_number)

            # Click CONTINUE
            page.locator("button:has-text('CONTINUE')").click()
            print("Phone number submitted. Waiting for OTP page...")
        else:
            print("Flipkart phone number input not found!")
            return

        # WAIT FOR OTP INPUT PAGE
        page.wait_for_selector("text=Enter OTP", timeout=10000)

        # SECOND STEP → OTP input
        otp_input = None

        try:
            otp_input = page.get_by_label("Enter OTP")
        except:
            pass

        if not otp_input or otp_input.count() == 0:
            otp_input = page.locator("input[maxlength='6']")

        if otp_input.count() == 0:
            print("OTP input not found!")
            return

        otp = input("Enter OTP received on phone: ")
        otp_input.fill(otp)

        # Click Login button
        page.locator("button:has-text('Login')").click()

        print("OTP submitted. Logged in!")

    except Exception as e:
        print(f"Flipkart login failed: {e}")



def amazon_login(page):
    """Prompt user to fill Amazon login if any valid email field is present."""
    try:
        # Email selectors Amazon commonly uses
        email_selectors = [
            "input#ap_email_login",
            "input#ap_email",
            "input[name='email']",
            "input[type='email']",
            "#ap_email_login",
        ]

        email_input = None

        # Try selectors in order
        for selector in email_selectors:
            loc = page.locator(selector)
            if loc.count() > 0:
                email_input = loc.first
                break

        if not email_input:
            print("Amazon login field not found.")
            return

        # Wait for visibility and fill
        email_input.wait_for(state="visible", timeout=5000)
        email = input("Enter your Amazon email: ")
        email_input.fill(email)

        # Continue button selectors
        continue_selectors = [
            "input#continue",
            "#continue",
            "input[type='submit'][aria-labelledby='continue']",
            "input[type='submit']",
            "button[type='submit']"
        ]

        continue_btn = None

        # Try locating continue button
        for selector in continue_selectors:
            loc = page.locator(selector)
            if loc.count() > 0:
                continue_btn = loc.first
                break

        if not continue_btn:
            print("Continue button not found.")
            return

        # Wait until button is enabled
        for _ in range(20):  # retry up to 2 seconds
            if continue_btn.is_enabled():
                break
            page.wait_for_timeout(100)

        # Now click the continue button
        continue_btn.click(force=True)
        print("Filled Amazon email and clicked Continue")

        # -------------------------------------------------
        # NEW: PASSWORD FIELD + SIGN-IN BUTTON
        # -------------------------------------------------

        # Wait for password field to appear
        password_field = page.locator("#ap_password")

        password_field.wait_for(state="visible", timeout=8000)

        pwd = input("Enter your Amazon password: ")
        password_field.fill(pwd)
        print("Filled Amazon password")

        # Sign-in button selectors
        sign_in_selectors = [
            "#signInSubmit",
            "input#signInSubmit",
            "button#signInSubmit",
            "input[type='submit'][aria-labelledby='signInSubmit']",
            "button[type='submit']"
        ]

        sign_in_btn = None

        for selector in sign_in_selectors:
            loc = page.locator(selector)
            if loc.count() > 0:
                sign_in_btn = loc.first
                break

        if not sign_in_btn:
            print("Sign-in button not found.")
            return

        # Wait until enabled
        for _ in range(20):
            if sign_in_btn.is_enabled():
                break
            page.wait_for_timeout(100)

        # Click sign in
        sign_in_btn.click(force=True)
        print("Clicked Sign-In button")

    except Exception as e:
        print(f"Amazon login failed: {e}")


def open_page(url):
    """
    Clicks Add to Cart / Buy Now and then prompts user to fill login if necessary.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)

        # List of common selectors for "Add to Cart" / "Buy Now"
        selectors = [
            # Amazon
            "button#add-to-cart-button",
            "input#buy-now-button",
            "button:has-text('Add to Cart')",
            "button:has-text('Buy Now')",
            
            # Flipkart
            "button._2KpZ6l._2U9uOA._3v1-ww",
            "button._2KpZ6l._2U9uOA._3v1-ww:has-text('Buy Now')",
            
            # Google Store
            "button[jsname='LgbsSe']",
            "button:has-text('Add to Cart')",
            "button:has-text('Buy')",
            
            # Apple Store
            "button.add-to-cart",
            "button:has-text('Add to Bag')",
            "button:has-text('Buy')",
            
            # Generic
            "a:has-text('Add to Cart')",
            "a:has-text('Buy Now')",
            "[role='button']:has-text('Add to Cart')",
            "[role='button']:has-text('Buy Now')"
        ]

        clicked = False
        for selector in selectors:
            try:
                button = page.locator(selector)
                if button.count() == 0:
                    continue
                button.wait_for(state="visible", timeout=5000)
                button.scroll_into_view_if_needed()
                button.click()
                print(f"Clicked button using selector: {selector}")
                clicked = True
                break
            except Exception as e:
                print(f"Failed to click {selector}: {e}")

        if not clicked:
            print("No clickable Add to Cart / Buy Now button found.")
            browser.close()
            return

        page.wait_for_timeout(3000)

        # Detect login pages and prompt user
        if "flipkart" in url:
            flipkart_login(page)
        elif "amazon" in url:
            amazon_login(page)
        else:
            print("No login automation available for this site.")

        # Keep browser open to see the result
        page.wait_for_timeout(10000)
        browser.close()


# Example usage
my_url = input("Enter the product URL: ")
open_page(my_url)
