from playwright.async_api import async_playwright
from openai import OpenAI
import asyncio
from dotenv import load_dotenv
load_dotenv()
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ask_ai_to_find_selector(html, purpose):
    """AI extracts selector for a button or field when unknown."""
    prompt = f"""
You are a DOM automation expert. Identify the BEST css selector for the element that represents:

ACTION: "{purpose}"

Return ONLY the selector text (ex: `button.buy-now`, `input[name=email]`).
HTML Snapshot (trimmed):
{html[:5000]}
"""
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role":"user","content":prompt}]
    )
    return response.choices[0].message.content.strip()


async def find_element(page, labels):
    """Try smart matching, fallback to AI if needed."""
    for label in labels:
        try:
            el = page.get_by_text(label)
            if await el.count() > 0:
                return el.first
        except:
            pass

        try:
            el = page.get_by_role("button", name=label)
            if await el.count() > 0:
                return el.first
        except:
            pass

    # AI Fallback
    selector = await ask_ai_to_find_selector(await page.content(), labels[0])
    return page.locator(selector)


async def find_input_field(page, keywords):
    """Locate a fillable input field using placeholder, type, or AI if needed."""
    
    # 1️⃣ Match placeholder text
    for word in keywords:
        inp = page.locator(f"input[placeholder*='{word}']")
        if await inp.count() > 0:
            return inp.first

    # 2️⃣ Match common text inputs
    inp = page.locator("input[type='text'], input[type='tel'], input[type='email'], input[type='password']")
    if await inp.count() > 0:
        return inp.first

    # 3️⃣ Consider contenteditable input for OTP fields
    editable = page.locator("[contenteditable='true']")
    if await editable.count() > 0:
        return editable.first

    # 4️⃣ AI fallback
    selector = await ask_ai_to_find_selector(await page.content(), f"input field for {keywords[0]}")
    return page.locator(selector)


async def detect_login_type(page):
    """Identify login mechanism based on editable fields."""
    html = (await page.content())[:5000] 
    prompt = f"""
Analyze the following HTML and identify the login method:

Options:
1. email_password
2. username_password
3. phone_otp
4. multi_step (phone/email -> continue -> password)
5. social_only (google login etc)

Return ONLY one word from the list above.

HTML:
{html}
"""
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

    return response.strip()


async def login_flow(page):
    login_type = await detect_login_type(page)
    print(f"🔍 Detected login type: {login_type}")

    # ---------------- EMAIL / USERNAME + PASSWORD ----------------
    if login_type in ["email_password", "username_password"]:
        username = input("📧 Enter email/username: ")
        password = input("🔑 Enter password: ")

        email_field = await find_input_field(page, ["Email", "Username", "Phone", "Mobile"])
        await email_field.fill(username)

        pass_field = await find_input_field(page, ["Password", "Pass"])
        await pass_field.fill(password)

        login_btn = await find_element(page, ["Login", "Sign in", "Continue", "Next"])
        await login_btn.click()

        await asyncio.sleep(3)
        print("✔ Logged in (if credentials were correct).")


    # ---------------- PHONE LOGIN + OTP ----------------
    elif login_type == "phone_otp":
        phone = input("📱 Enter phone number: ")
        
        phone_field = await find_input_field(page, ["Phone", "Mobile", "Number"])
        await phone_field.fill(phone)

        continue_btn = await find_element(page, ["Next", "Continue", "Send OTP"])
        await continue_btn.click()

        print("📨 Waiting for OTP...")
        otp = input("Enter OTP received: ")

        otp_inputs = page.locator("input[type='text'], input[type='tel'], input[autocomplete='one-time-code']")
        count = await otp_inputs.count()

        if count == 1:
            await otp_inputs.first.fill(otp)
        else:
            for i, digit in enumerate(otp):
                await otp_inputs.nth(i).fill(digit)

        await asyncio.sleep(2)
        print("✔ OTP Verified.")


    # ---------------- MULTI STEP LOGIN ----------------
    elif login_type == "multi_step":
        identifier = input("📧 Enter email / phone: ")

        field = await find_input_field(page, ["Email", "Phone", "Mobile", "Username"])
        await field.fill(identifier)

        next_btn = await find_element(page, ["Next", "Continue"])
        await next_btn.click()

        await asyncio.sleep(2)
        return await login_flow(page)


    # ---------------- SOCIAL LOGIN ----------------
    elif login_type == "social_only":
        print("⚠ This site requires Google / Apple login.")
        input("Press ENTER after logging in manually...")
        return "manual"

    return "ok"


async def login_available(page):
    btn = page.locator("text=Login, text=Sign in, text=Continue")
    if await btn.count() > 0:
        return True

    inputs = page.locator("input[type='text'], input[type='email'], input[type='tel'], input[placeholder*='phone'], input[placeholder*='email']")
    if await inputs.count() > 0:
        return True

    if await page.locator("input[type='password']").count() > 0:
        return True

    return False


async def find_store_url(query: str):
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {
                "role": "system",
                "content": """Extract ONLY a valid official shopping URL based on user intent.

Examples:
"buy iphone from apple store" -> https://www.apple.com/store
"buy samsung s24" -> https://www.samsung.com/in
"order pizza" -> https://www.dominos.com

Return ONLY the URL. No extra text."""
            },
            {"role": "user", "content": query}
        ]
    )

    return response.choices[0].message.content.strip()


async def find_and_open_product(page, product_name):
    print("🔍 Searching for product on the page...")

    product_locator = page.get_by_text(product_name, exact=False)

    if await product_locator.count() > 0:
        print("📦 Product found on homepage. Opening...")
        await product_locator.first.click()
        await asyncio.sleep(3)
        return True

    print("🔍 Product not visible. Trying search bar...")

    search_field = await find_input_field(page, ["Search", "Product", "Find", "Looking"])
    await search_field.fill(product_name)
    await page.keyboard.press("Enter")
    await asyncio.sleep(3)

    result = page.locator(f"a:has-text('{product_name[:10]}')")

    if await result.count() > 0:
        print("📄 Opening first search result...")
        await result.first.click()
        await asyncio.sleep(3)
        return True

    return False



async def run_automation(query: str):
    print(f"🤖 Understanding request: {query}")
    
    intent_response = client.chat.completions.create(
        model="gpt-5.1",
        temperature=0,
        messages=[
            {"role":"system","content":"""
You are an intent detector. From user text extract:
{
 "task_type":"buy" | "movie" | "form" | "unknown",
 "url": "detected website url or null",
 "item": "name of product/movie/ticket if any"
}
Return valid JSON only.
"""},
            {"role":"user","content":query}
        ]
    )

    intent = intent_response.choices[0].message.content

    try:
        info = json.loads(intent)
    except:
        return "⚠ Couldn't understand the request."

    url = info.get("url")
    product_name = info.get("item", "unknown item")

    if not url:
        return "❌ No URL detected. User must provide a link."

    print(f"🌍 Navigating to: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=120)
        context = await browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    viewport={"width":1280, "height":800}
)
        page = await context.new_page()

        await page.goto(url)
        try:
           await page.wait_for_load_state("domcontentloaded")
        except:
            pass
        await asyncio.sleep(3)
        print("🧭 Page loaded.")

        login_needed = input("🔐 Do you need to log in? (yes/no): ").strip().lower()

        if login_needed == "yes":
            print("🔎 Checking if login is available on this page...")
            
            if await login_available(page):
                print("✅ Login form detected. Proceeding...")
                await login_flow(page)
            else:
                print("⚠ No login option detected. Continuing without login...")

        print("⌛ Attempting product search...")
        found = await find_and_open_product(page, product_name)

        if not found:
            print("❌ Could not find product automatically.")
            return

        next_button = await find_element(page, ["Buy Now", "Add to Cart", "Book Tickets", "Next", "Continue"])
        await next_button.click()

        await asyncio.sleep(4)

        print("💳 Stopping here due to security rules.")
        print(f"➡ Payment page opened: {page.url}")

        if await login_available(page):
            print("🔑 Login required for checkout — starting...")
            await login_flow(page)

        return page.url


if __name__ == "__main__":
    query = input("Ask me: ")
    result = asyncio.run(run_automation(query))
    print(result)
