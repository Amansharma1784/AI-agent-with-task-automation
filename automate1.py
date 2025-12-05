import asyncio
from playwright.async_api import async_playwright

async def main():
    product_url = input("Enter the product URL: ")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Visiting: {product_url}")
        await page.goto(product_url)

        # Example: Try to click 'Add to Cart' button
        # These selectors may need to be adjusted for each site
        add_to_cart_selectors = [
            "button#add-to-cart-button",                 # Amazon
            "button[data-test='add-to-cart']",           # Flipkart
            "button:has-text('Add to Bag')",            # Apple
        ]

        added = False
        for selector in add_to_cart_selectors:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.click()
                    print(f"Clicked Add to Cart: {selector}")
                    added = True
                    break
            except:
                continue

        if not added:
            print("Could not find Add to Cart button automatically. Please add manually.")

        # Keep browser open so user can continue checkout
        await page.wait_for_timeout(30000)  # 30 seconds

        await browser.close()

asyncio.run(main())
