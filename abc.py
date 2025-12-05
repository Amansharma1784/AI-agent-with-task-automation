from playwright.sync_api import sync_playwright

PHONE = "8168874188"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://www.flipkart.com/login")

    # Click Login
    page.click("a._1_3w1N")

    # Enter phone number
    page.fill("input[placeholder='Enter Email/Mobile number']", PHONE)

    # Click Continue (request OTP)
    page.click("button._2KpZ6l._2HKlqd._3AWRsL")

    # Wait for OTP screen to appear
    page.wait_for_selector("input._2IX_2-._3mctLh")

    otp = input("Enter OTP sent to your phone: ")

    # Fill the OTP
    page.fill("input._2IX_2-._3mctLh", otp)

    page.press("input._2IX_2-._3mctLh", "Enter")

    print("Logged in!")

    input("Press Enter to close browser...")
    browser.close()
