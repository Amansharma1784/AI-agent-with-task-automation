
from agno.tools import tool
from playwright.async_api import async_playwright
import time
import json

async def wait_for_manual_login(page, success_url_substring=None, timeout=300):
    """
    Wait for user to manually complete login.
    success_url_substring = a part of URL that confirms login (optional)
    timeout = max wait time in seconds
    """
    
    print("\n🔐 Waiting for manual login...")
    print("👉 Please enter credentials and complete login (OTP/Password/etc).")
    print(f"⏳ Timeout: {timeout} seconds\n")

    start = time.time()

    while time.time() - start < timeout:
        current_url = page.url
        
        # If a success pattern provided, detect login success
        if success_url_substring and success_url_substring in current_url:
            print("🎉 Login detected by URL change!")
            return True

        # More generic detection: Look for logout / account icon after login
        possible_logged_in_indicators = [
            "Logout", "Log Out", "My Account", "Profile", "Orders", "Account"
        ]

        for keyword in possible_logged_in_indicators:
            el = page.locator(f"text={keyword}")
            if await el.count() > 0:
                print(f"🎉 Login detected ({keyword} found)")
                return True

        await page.wait_for_timeout(2000)

    print("⚠️ Login not completed within timeout.")
    return False



async def start_and_login(input_data) -> str:

    print("===========",input_data)
    url = None
    if isinstance(input_data, str):
        url = input_data
    
    elif isinstance(input_data, dict):
        # Try common keys
        url = input_data.get("url") or input_data.get("link") or input_data.get("input")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context()

        # Load previous session if exists
        try:
            with open("session.json", "r") as f:
                context = await browser.new_context(storage_state="session.json")
                print("✔ Loaded saved session (might bypass login).")
        except:
            pass

        page = await context.new_page()
        await page.goto(url)

        # Wait for user login manually
        logged_in = await wait_for_manual_login(page, timeout=300)

        if logged_in :
            # Save cookies and session for next time
            storage = await context.storage_state()
            with open("session.json", "w") as f:
                json.dump(storage, f, indent=2)
            print("💾 Session saved. Next login may be automatic.")

        print("\n🚀 Moving forward... browser stays open for further actions.")
        _ = input("\nPress ENTER to close browser manually.\n")

    return "completed"



# Example usage
# start_and_login("https://www.flipkart.com")


from agno.tools import tool
from playwright.async_api import async_playwright
import os, asyncio, json

@tool
async def buy_product(input_data) -> str:
    """Open product page → click Buy / Add to cart → go to checkout."""
    
    # Normalize URL input
    url = input_data if isinstance(input_data, str) else input_data.get("url")

    if not url:
        return "❌ No product URL found."

    print(f"\n📦 Opening product page: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=80)

        # Load saved login session
        if os.path.exists("session.json"):
            context = await browser.new_context(storage_state="session.json")
            print("🔑 Logged-in session restored.")
        else:
            return "⚠️ You must run login tool first."

        page = await context.new_page()
        await page.goto(url)

        # Scroll to ensure buttons load
        await page.mouse.wheel(0, 800)
        await asyncio.sleep(2)

        # Possible selectors for buy buttons
        selectors = [
            "button:has-text('Buy Now')",
            "button:has-text('BUY NOW')",
            "button:has-text('Add to Cart')",
            "button:has-text('ADD TO CART')",
            "[data-testid='buy-button']",
            "[data-testid='add-to-cart-button']",
        ]

        clicked = False
        for selector in selectors:
            try:
                locator = page.locator(selector)
                if await locator.count() > 0:
                    await locator.first.click()
                    print(f"🛒 Clicked: {selector}")
                    clicked = True
                    break
            except:
                continue

        if not clicked:
            return "❌ Couldn't find Buy or Add-to-Cart button."

        await asyncio.sleep(4)

        # Go to checkout page
        checkout_selectors = [
            "button:has-text('Place Order')",
            "button:has-text('Proceed to Checkout')",
            "[data-testid='place-order-button']"
        ]

        for selector in checkout_selectors:
            locator = page.locator(selector)
            if await locator.count() > 0:
                await locator.first.click()
                print("🚚 Proceeding to checkout...")
                break
        
        print("\n💳 Payment page reached. Complete payment manually.")

        # keep the page open
        while True:
            await asyncio.sleep(5)

    return "Checkout complete (manual payment required)."






from agno.tools import tool
from playwright.async_api import async_playwright
import re, os, asyncio

def extract_details(query: str):
    """Simple NLP extraction from user sentence."""
    
    movie_match = re.search(r"(book|reserve).*(?:for )(.+?)(?: in| at| on| tomorrow| today)", query, re.IGNORECASE)
    movie = movie_match.group(2) if movie_match else None

    city_match = re.search(r"in ([A-Za-z ]+)", query)
    city = city_match.group(1).strip() if city_match else "Delhi"

    seats_match = re.search(r"(\d+) (seat|ticket)", query)
    seats = int(seats_match.group(1)) if seats_match else 1

    if "tomorrow" in query.lower():
        date = "Tomorrow"
    else:
        date = "Today"

    # time preference heuristic
    if "evening" in query.lower():
        time_pref = "PM"
    elif "morning" in query.lower():
        time_pref = "AM"
    else:
        time_pref = ""

    return movie, city, date, time_pref, seats



from agno.tools import tool
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import os, asyncio

def parse_url(url: str):
    parts = urlparse(url).path.split("/")
    city = parts[1] if len(parts) > 1 else None
    movie = parts[3] if len(parts) > 3 else None
    return movie, city


@tool
async def book_movie_ticket(url: str) -> str:
    """Book movie ticket using booking URL and proceed until payment page."""

    print(f"🔗 Booking URL received: {url}")

    movie, city = parse_url(url)
    seats = 1   # default
    date = "Today"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)

        if not os.path.exists("session.json"):
            return "⚠️ Login session missing. Run login tool first."

        context = await browser.new_context(storage_state="session.json")
        page = await context.new_page()
        await page.goto(url)

        print(f"🎬 Movie: {movie}")
        print(f"📍 City: {city}")

        # Direct booking flow
        await asyncio.sleep(3)

        # Select first available timing
        showtimes = page.locator("a.showtime-pill")
        await showtimes.first.click()

        await asyncio.sleep(3)

        # pick seat
        await page.locator(".__seat.__available").first.click()

        await asyncio.sleep(2)
        await page.get_by_role("button", name="Proceed").click()

        final_url = page.url

        return f"🎟 Ticket reserved.\n💳 Complete payment: {final_url}"
