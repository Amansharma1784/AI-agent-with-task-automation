from nicegui import ui
import httpx

API_URL = "http://127.0.0.1:8081/routes/search"

ui.colors(primary='#4f46e5')  # Indigo accent

ui.add_head_html("""
<style>
.chat-container {
    max-height: 75vh;
    overflow-y: auto;
    padding: 20px;
    background: #f8fafc;
    border-radius: 12px;
    border: 1px solid #d1d5db;
}
.user-bubble {
    background: #4f46e5;
    color: white;
    padding: 10px 14px;
    border-radius: 14px;
    max-width: 70%;
    margin-left: auto;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.bot-bubble {
    background: white;
    color: black;
    padding: 10px 14px;
    border-radius: 14px;
    max-width: 70%;
    margin-right: auto;
    margin-bottom: 10px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.input-box {
    width: 100%;
    border-radius: 12px;
}
</style>
""")

ui.markdown("""
### 🎬 AI Ticket Booking Chatbot  
Type something like **_Book 2 tickets for Leo tomorrow in Mumbai_**
""").classes('text-center text-xl mt-4')

messages = ui.column().classes('chat-container')

with ui.footer().classes('w-full p-4 flex gap-3 bg-white border-t'):
    input_box = ui.input(
        placeholder="Type your message..."
    ).props('outlined').classes('input-box')
    
    send_button = ui.button("Send", color="primary")


async def send_message():
    text = input_box.value.strip()
    if not text:
        return

    # Show user message bubble
    with messages:
        ui.html(f'<div class="user-bubble">🧑 {text}</div>',sanitize=False)

    input_box.value = ""
    await ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")

    # Bot thinking bubble placeholder
    bubble = ui.html('<div class="bot-bubble">🤖 Thinking...</div>',sanitize=False)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, params={"q": text})
            data = response.json()
            bubble.text = f'<div class="bot-bubble">🤖 {data.get("response", "⚠ No response.")}</div>'
        except Exception as e:
            bubble.text = f'<div class="bot-bubble">⚠ Error: {e}</div>'

    # auto scroll to last message
    await ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")


# make Enter key work
input_box.on('keydown.enter', lambda e: send_message())

# button click
send_button.on_click(send_message)

# Dark mode toggle
ui.button("🌙 / ☀️", on_click=lambda: ui.dark_mode.toggle()).classes('absolute top-4 right-4 text-sm')

ui.run(port=8082, title="AI Assistant")
