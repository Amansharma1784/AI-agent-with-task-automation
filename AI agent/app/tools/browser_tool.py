
# from agno.tools import tool
# from playwright.async_api import async_playwright
# import time
# import json

# async def wait_for_manual_login(page, success_url_substring=None, timeout=300):
#     """
#     Wait for user to manually complete login.
#     success_url_substring = a part of URL that confirms login (optional)
#     timeout = max wait time in seconds
#     """
    
#     print("\n🔐 Waiting for manual login...")
#     print("👉 Please enter credentials and complete login (OTP/Password/etc).")
#     print(f"⏳ Timeout: {timeout} seconds\n")

#     start = time.time()

#     while time.time() - start < timeout:
#         current_url = page.url
        
#         # If a success pattern provided, detect login success
#         if success_url_substring and success_url_substring in current_url:
#             print("🎉 Login detected by URL change!")
#             return True

#         # More generic detection: Look for logout / account icon after login
#         possible_logged_in_indicators = [
#             "Logout", "Log Out", "My Account", "Profile", "Orders", "Account"
#         ]

#         for keyword in possible_logged_in_indicators:
#             el = page.locator(f"text={keyword}")
#             if await el.count() > 0:
#                 print(f"🎉 Login detected ({keyword} found)")
#                 return True

#         await page.wait_for_timeout(2000)

#     print("⚠️ Login not completed within timeout.")
#     return False



# async def start_and_login(input_data) -> str:

#     print("===========",input_data)
#     url = None
#     if isinstance(input_data, str):
#         url = input_data
    
#     elif isinstance(input_data, dict):
#         # Try common keys
#         url = input_data.get("url") or input_data.get("link") or input_data.get("input")

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False, slow_mo=100)
#         context = await browser.new_context()

#         # Load previous session if exists
#         try:
#             with open("session.json", "r") as f:
#                 context = await browser.new_context(storage_state="session.json")
#                 print("✔ Loaded saved session (might bypass login).")
#         except:
#             pass

#         page = await context.new_page()
#         await page.goto(url)

#         # Wait for user login manually
#         logged_in = await wait_for_manual_login(page, timeout=300)

#         if logged_in :
#             # Save cookies and session for next time
#             storage = await context.storage_state()
#             with open("session.json", "w") as f:
#                 json.dump(storage, f, indent=2)
#             print("💾 Session saved. Next login may be automatic.")

#         print("\n🚀 Moving forward... browser stays open for further actions.")
#         _ = input("\nPress ENTER to close browser manually.\n")

#     return "completed"



# # Example usage
# # start_and_login("https://www.flipkart.com")


# from agno.tools import tool
# from playwright.async_api import async_playwright
# import os, asyncio, json

# @tool
# async def buy_product(input_data) -> str:
#     """Open product page → click Buy / Add to cart → go to checkout."""
    
#     # Normalize URL input
#     url = input_data if isinstance(input_data, str) else input_data.get("url")

#     if not url:
#         return "❌ No product URL found."

#     print(f"\n📦 Opening product page: {url}")

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False, slow_mo=80)

#         # Load saved login session
#         if os.path.exists("session.json"):
#             context = await browser.new_context(storage_state="session.json")
#             print("🔑 Logged-in session restored.")
#         else:
#             return "⚠️ You must run login tool first."

#         page = await context.new_page()
#         await page.goto(url)

#         # Scroll to ensure buttons load
#         await page.mouse.wheel(0, 800)
#         await asyncio.sleep(2)

#         # Possible selectors for buy buttons
#         selectors = [
#             "button:has-text('Buy Now')",
#             "button:has-text('BUY NOW')",
#             "button:has-text('Add to Cart')",
#             "button:has-text('ADD TO CART')",
#             "[data-testid='buy-button']",
#             "[data-testid='add-to-cart-button']",
#         ]

#         clicked = False
#         for selector in selectors:
#             try:
#                 locator = page.locator(selector)
#                 if await locator.count() > 0:
#                     await locator.first.click()
#                     print(f"🛒 Clicked: {selector}")
#                     clicked = True
#                     break
#             except:
#                 continue

#         if not clicked:
#             return "❌ Couldn't find Buy or Add-to-Cart button."

#         await asyncio.sleep(4)

#         # Go to checkout page
#         checkout_selectors = [
#             "button:has-text('Place Order')",
#             "button:has-text('Proceed to Checkout')",
#             "[data-testid='place-order-button']"
#         ]

#         for selector in checkout_selectors:
#             locator = page.locator(selector)
#             if await locator.count() > 0:
#                 await locator.first.click()
#                 print("🚚 Proceeding to checkout...")
#                 break
        
#         print("\n💳 Payment page reached. Complete payment manually.")

#         # keep the page open
#         while True:
#             await asyncio.sleep(5)

#     return "Checkout complete (manual payment required)."




# from agno.tools import tool
# from playwright.async_api import async_playwright
# from urllib.parse import urlparse
# import os, asyncio

# def parse_url(url: str):
#     parts = urlparse(url).path.split("/")
#     city = parts[1] if len(parts) > 1 else None
#     movie = parts[3] if len(parts) > 3 else None
#     return movie, city


# @tool
# async def book_movie_ticket(url: str) -> str:
#     """Book movie ticket using booking URL and proceed until payment page."""

#     print(f"🔗 Booking URL received: {url}")

#     movie, city = parse_url(url)
#     seats = 1   # default
#     date = "Today"

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False, slow_mo=100)

#         if not os.path.exists("session.json"):
#             return "⚠️ Login session missing. Run login tool first."

#         context = await browser.new_context(storage_state="session.json")
#         page = await context.new_page()
#         await page.goto(url)

#         print(f"🎬 Movie: {movie}")
#         print(f"📍 City: {city}")

#         # Direct booking flow
#         await asyncio.sleep(3)

#         # Select first available timing
#         showtimes = page.locator("a.showtime-pill")
#         await showtimes.first.click()

#         await asyncio.sleep(3)

#         # pick seat
#         await page.locator(".__seat.__available").first.click()

#         await asyncio.sleep(2)
#         await page.get_by_role("button", name="Proceed").click()

#         final_url = page.url

#         return f"🎟 Ticket reserved.\n💳 Complete payment: {final_url}"





from playwright.sync_api import sync_playwright
from agno.tools import tool




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



@tool
def buy_product(url: str) -> str:
    print("=-===============", url)
    """
    Opens a web page and tries to click an "Add to Cart" or "Buy Now" button.
    Returns a message indicating success or failure.
    """
    try:
        p = sync_playwright().start() 
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to the URL
        page.goto(url)
        
        # Wait a few seconds for dynamic content
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
        clicked_selector = None

        # Try each selector until one works
        for selector in selectors:
            try:
                button = page.locator(selector)
                if button.count() == 0:
                    continue

                button.wait_for(state="visible", timeout=5000)
                button.scroll_into_view_if_needed()
                button.click()
                clicked = True
                clicked_selector = selector

                # Wait for redirection to login page
                page.wait_for_timeout(2000)

                # Run login if needed
                if "flipkart" in url:
                    flipkart_login(page)
                elif "amazon" in url:
                    amazon_login(page)
                else:
                    print("No login automation available for this site.")

                break  # stop trying other selectors after click
            except Exception:
                continue

        if clicked:
            return f"Clicked button using selector: {clicked_selector}. Browser remains open for manual checkout."
        else:
            return "No clickable Add to Cart / Buy Now button found."

    except Exception as e:
        return f"Error occurred: {e}"




import re



def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())

def find_theatre(page, theatre_name):
    target = normalize(theatre_name)
    seen = set()
    last_scroll = -1

    for _ in range(300):
        blocks = page.locator("div.hStBrg")
        count = blocks.count()
        for i in range(count):
            block = blocks.nth(i)
            name_el = block.locator("span.sc-1qdowf4-0.kVfEkA")
            if name_el.count() == 0:
                continue
            name = name_el.inner_text().strip()
            norm_name = normalize(name)
            if norm_name in seen:
                continue
            seen.add(norm_name)
            print("Checking:", name)
            if target in norm_name:
                print(f"✅ Matched theatre: {name}")
                return block

        # Scroll down
        page.evaluate("""
            () => {
                let el = document.querySelector(".ReactVirtualized__Grid__innerScrollContainer");
                el.parentElement.scrollBy(0, 400);
            }
        """)
        time.sleep(0.25)

        scroll_now = page.evaluate("""
            () => document.querySelector(".ReactVirtualized__Grid__innerScrollContainer").parentElement.scrollTop
        """)
        if scroll_now == last_scroll:
            break
        last_scroll = scroll_now

    return None

def find_showtime(theatre_block, show_time):
    target = normalize(show_time)
    show_buttons = theatre_block.locator("div.sc-1vhizuf-2.jIiAgZ")
    for i in range(show_buttons.count()):
        text = show_buttons.nth(i).inner_text().strip()
        if normalize(text) == target:
            return show_buttons.nth(i)
    return None


@tool
def book_movie_ticket(movie_url: str, theatre_name: str, show_time: str) -> str:
    """
    Book movie ticket tool that navigates BookMyShow, selects theatre, showtime,
    clicks select seats button and loads seat layout page.

    Returns a status string.
    """
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False, slow_mo=40)
            page = browser.new_page()

            print("Opening movie page...")
            page.goto(movie_url, wait_until="networkidle")
            page.wait_for_selector("div.ReactVirtualized__Grid__innerScrollContainer")

            print("\n---- Searching theatre ----")
            theatre_block = find_theatre(page, theatre_name)
            if not theatre_block:
                return "❌ Theatre not found!"

            print("\n---- Searching showtime ----")
            show_button = find_showtime(theatre_block, show_time)
            if not show_button:
                return "❌ Show time not found in this theatre!"

            print("🎬 Clicking showtime:", show_time)
            show_button.click()

            # Wait for the "How many seats?" popup to appear
            page.wait_for_selector("button:has-text('Select Seats')", timeout=10000)

            print("🎯 Clicking 'Select Seats' button...")
            page.locator("button:has-text('Select Seats')").click()

            page.wait_for_load_state("networkidle")
            print("🎉 Reached seat layout page!")

            return f"✅ Navigated to seat layout page for '{theatre_name}' at {show_time}."

    except Exception as e:
        return f"Error occurred: {e}"
