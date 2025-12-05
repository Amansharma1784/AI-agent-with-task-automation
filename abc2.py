from playwright.sync_api import sync_playwright
import time
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

def book_ticket(movie_url, theatre_name, show_time):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=40)
        page = browser.new_page()

        print("Opening movie page...")
        page.goto(movie_url, wait_until="networkidle")
        page.wait_for_selector("div.ReactVirtualized__Grid__innerScrollContainer")

        print("\n---- Searching theatre ----")
        theatre_block = find_theatre(page, theatre_name)
        if not theatre_block:
            print("❌ Theatre not found!")
            return

        print("\n---- Searching showtime ----")
        show_button = find_showtime(theatre_block, show_time)
        if not show_button:
            print("❌ Show time not found in this theatre!")
            return

        print("🎬 Clicking showtime:", show_time)
        show_button.click()
        # Wait for the "How many seats?" popup to appear
        page.wait_for_selector("button:has-text('Select Seats')", timeout=10000)  # wait max 10s

        print("🎯 Clicking 'Select Seats' button...")
        page.locator("button:has-text('Select Seats')").click()
        

        page.wait_for_load_state("networkidle")
        print("🎉 Reached seat layout page!")

        # You can add code here to select specific seats if you want
        time.sleep(5)

        print("🎉 Reached seat selection page!")

        time.sleep(5)

# Example usage
book_ticket(
    movie_url="https://in.bookmyshow.com/movies/chandigarh/tere-ishk-mein/buytickets/et00362760/20251205",
    theatre_name="centra",   # partial name works now
    show_time="07:25 PM"
)
