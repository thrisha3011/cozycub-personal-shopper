from flask import Flask, request, jsonify, render_template_string, send_from_directory

from playwright.sync_api import sync_playwright
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List
from PIL import Image
import re
import json
import os
import time

app = Flask(__name__)

# Ensure local static asset directory exists to cache screenshots safely
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# --- CONFIGURATION: Non-vision model for super-fast text intent parsing ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

try:
    if GROQ_API_KEY and not GROQ_API_KEY.startswith("gsk_YOUR_REAL"):
        llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile", temperature=0.1)
    else:
        llm = None
except Exception as e:
    print(f" Groq initialization bypassed: {str(e)}")
    llm = None

# --- STATEFUL SESSION RUNTIME DATABASE ---
SESSION_STATE = {
    "payment_ready": False,
    "chat_history": []
}

# --- ADVANCED STRUCTURAL INTENT Blueprints ---
class ShoppingItem(BaseModel):
    search_query: str = Field(description="The exact query to type into the search bar, maintaining structural parameters like 'tomato 1kg', 'kurkure rs 10', 'milk 1l', or 'oreo'")
    click_count: int = Field(default=1, description="The number of times the ADD button must be pressed for this item based on requested packs/quantities")

class GroqResponseSchema(BaseModel):
    is_shopping_intent: bool = Field(description="True if the user intent states a desire to look up, track, or buy groceries")
    items_array: List[ShoppingItem] = Field(description="List of items parsed with targeted search strings and active quantities")
    conversational_reply: str = Field(description="A clean, friendly natural text greeting without unescaped inner quotation marks")


def crop_screenshot_to_cart_panel(raw_image_path: str):
    """Isolates the right-hand layout panel overlay cleanly using absolute coordinate definitions."""
    try:
        time.sleep(1) 
        img = Image.open(raw_image_path)
        img_width, img_height = img.size
        
        left = int(img_width * 0.64)   
        top = 0                         
        right = img_width               
        bottom = img_height             
        
        area = (left, top, right, bottom)
        cropped_img = img.crop(area)
        cropped_img.save(raw_image_path)
        print(" Cart frame canvas isolated cleanly via Pillow area crop vectors!")
    except Exception as e:
        print(f" [Pillow Crop Processor Exception]: {str(e)}")


def run_playwright_simulation(items_list: list):
    """PHASE 1: INSTANT RUN AUTOMATION LOOP (ROBUST CLOUD PRODUCTION ENVIRONMENT)"""
    print("\n[Playwright Engine] Running Headless Cloud Sourcing Automation...")
    screenshot_path = os.path.join(STATIC_DIR, "latest_checkout_cart.png")
    
    with sync_playwright() as p:
        try:
            # ROBUST CLOUD FLAGS: Ensures Chromium runs without a desktop layer on Render Linux instances
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox", 
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process"
                ]
            )
            
            # Set a standard desktop window size for the background canvas
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()
            
            print("Navigating to https://blinkit.com")
            page.goto("https://blinkit.com", timeout=60000)
            time.sleep(5)
            
            # Location Setup
            print("Locating Address Input Container...")
            location_input = page.locator("//input[@placeholder='search delivery location']").first
            if location_input.is_visible(timeout=5000):
                location_input.click()
                location_input.type("PSG Tech, Peelamedu, Coimbatore", delay=100)
                time.sleep(4) 
                
                first_suggestion = page.locator("//div[contains(@class, 'LocationSearchList__LocationLabel')]").first
                if first_suggestion.is_visible(timeout=5000):
                    first_suggestion.click(force=True)
                    print("Manual Location Selection Confirmed Successfully.")
                    time.sleep(6) 
            
            # Smart Multi-Product Sourcing Automation
            for item in items_list:
                smart_query = item.get("search_query", "").strip()
                target_clicks = item.get("click_count", 1)
                print(f"Searching optimized metric query string: '{smart_query}' | Action Loops: {target_clicks}")
                
                search_placeholder = page.locator("//div[contains(@class, 'SearchBar__PlaceholderContainer')] | //input[@placeholder='Search for atta dal and more']").first
                if search_placeholder.is_visible(timeout=5000):
                    search_placeholder.click(force=True)
                    time.sleep(1.5)
                
                main_search_bar = page.locator("//input[contains(@placeholder, 'Search')]").first
                if main_search_bar.is_visible(timeout=5000):
                    main_search_bar.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    main_search_bar.type(smart_query, delay=150)
                    time.sleep(3) 
                    
                    page.keyboard.press("Enter")
                    time.sleep(5)
                    
                    grid_add_button = page.locator("//div[text()='ADD'] | //div[text()='Add'] | //div[contains(@class, 'AddToCart')]").first
                    if grid_add_button.is_visible(timeout=5000):
                        grid_add_button.scroll_into_view_if_needed()
                        grid_add_button.click(force=True)
                        print(f"Item '{smart_query}' primary click added to viewport state.")
                        time.sleep(2.5) 
                        
                        for click_idx in range(target_clicks - 1):
                            plus_button = page.locator("//div[contains(@class, 'QuantityBlock')]//div[text()='+'] | //div[text()='+'] | //div[contains(@class, 'plus')]").first
                            if plus_button.is_visible(timeout=3000):
                                plus_button.click(force=True)
                                print(f"Clicked '+' to add product count multiplier: {click_idx + 2}")
                                time.sleep(1.5)
            
            # Expand Cart Drawer Summary View
            print("Opening live cart summary panel tray sheet...")
            my_cart_button = page.locator("//div[contains(., 'My Cart')] | //button[contains(., 'My Cart')] | //div[contains(@class, 'CartButton')]").first
            if my_cart_button.is_visible(timeout=5000):
                my_cart_button.click(force=True)
                time.sleep(4) 
                
            print("Snapping visual layout page grid viewport capture matrix...")
            page.screenshot(path=screenshot_path)
            browser.close()
            
            crop_screenshot_to_cart_panel(screenshot_path)
            
        except Exception as e:
            print(f"[Playwright Live Automation Exception]: {str(e)}")

@app.route('/static/<path:filename>')
def serve_static_assets(filename):
    return send_from_directory(STATIC_DIR, filename)

@app.route('/')
def chat_dashboard():
    return render_template_string(HTML_FRONTEND)


@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "I'm listening!"})

    user_lower = user_message.lower()

    if SESSION_STATE["payment_ready"]:
        if any(x in user_lower for x in ["accept", "yes", "pay", "ok", "accep"]):
            SESSION_STATE["payment_ready"] = False
            run_payment_success_simulation()
            return jsonify({"reply": " **Payment Gateway Sequence Concluded!**<br>Launched your simulated transaction success landing view frame layout completely!"})
        elif any(x in user_lower for x in ["reject", "cancel", "no"]):
            SESSION_STATE["payment_ready"] = False
            return jsonify({"reply": "Checkout loop aborted safely. What other items can I look up for you next?"})

    data = {"is_shopping_intent": False, "items_array": [], "conversational_reply": "Processing parameters..."}
    
    if llm:
        try:
            history_context = "\n".join([f"{m['sender']}: {m['text']}" for m in SESSION_STATE["chat_history"][-2:]])
            routing_prompt = (
                f"You are CozyCub, an AI shopping core manager. History:\n{history_context}\n"
                f"User text: '{user_message}'\n\n"
                "Extract requested items. Capture weights or metrics explicitly inside the search_query parameters. "
                "Map packet counts explicitly into click_count values."
            )
            structured_llm = llm.with_structured_output(GroqResponseSchema)
            res = structured_llm.invoke(routing_prompt)
            if res:
                data = res.model_dump()
        except Exception as e:
            print(f" [Groq Parsing Interception Failure]: {str(e)}")

    SESSION_STATE["chat_history"].append({"sender": "User", "text": user_message})

    if data.get("is_shopping_intent") and data.get("items_array"):
        # FIXED: Passes the extracted items array dictionary matching object definitions straight down
        run_playwright_simulation(data["items_array"])
        SESSION_STATE["payment_ready"] = True
        
        cache_buster = int(time.time())
        
        bot_reply = (
            f" **CozyCub:** {data.get('conversational_reply')}<br><br>"
            f" *Browser automation complete! Here is your cleanly cropped cart snippet matching your pixel boundary dimensions:*<br><br>"
            f"<div style='border: 2px solid #27272c; border-radius: 12px; overflow: hidden; max-width: 440px; margin: 10px auto; box-shadow: 0 8px 16px rgba(0,0,0,0.5);'>"
            f"  <img src='/static/latest_checkout_cart.png?v={cache_buster}' style='width: 100%; display: block;' alt='Isolated Cart Details'>"
            f"</div><br>"
            f" Type **'accept'** to confirm this visual summary and route directly to the Secure Payment Simulation Window!"
        )
        return jsonify({"reply": bot_reply})

    return jsonify({"reply": f" **CozyCub:** {data.get('conversational_reply', 'Let me know what items to source next!')}"})


# --- Chat Dashboard Layout Front-End HTML ---
HTML_FRONTEND = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CozyCub Autonomous Shopping Agent</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; }
        body { background: #0c0c0e; color: #e2e2e9; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 100%; max-width: 720px; height: 88vh; background: #131316; border: 1px solid #27272c; border-radius: 16px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.8); }
        .chat-header { background: #1a1a22; padding: 22px; text-align: center; border-bottom: 1px solid #27272c; }
        .chat-header h2 { color: #00e676; font-size: 1.45rem; font-weight: 600; }
        .chat-header p { font-size: 0.85rem; color: #a0a0b0; margin-top: 4px; }
        .chat-box { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; background: #0f0f12; }
        .msg { max-width: 82%; padding: 14px 18px; border-radius: 12px; font-size: 0.98rem; line-height: 1.6; word-wrap: break-word; }
        .user-msg { background: #008f58; color: #fff; align-self: flex-end; border-bottom-right-radius: 2px; }
        .agent-msg { background: #1e1e24; color: #e2e2e9; align-self: flex-start; border-bottom-left-radius: 2px; border: 1px solid #2a2a32; }
        .input-area { padding: 20px; background: #1a1a22; border-top: 1px solid #27272c; display: flex; gap: 12px; }
        .input-area input { flex: 1; padding: 16px; background: #0c0c0e; border: 1px solid #27272c; border-radius: 8px; color: #fff; font-size: 1rem; outline: none; }
        .input-area button { padding: 0 28px; background: #00e676; border: none; border-radius: 8px; color: #0c0c0e; font-weight: bold; font-size: 1rem; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2> CozyCub Smart Personal Shopper Sandbox</h2>
            <p>Smart Metric Slicing Multiplier Loop • Cropped Cart Verification Engine Active</p>
        </div>
        <div class="chat-box" id="chatBox">
            <div class="msg agent-msg">Hi! I am CozyCub. Type your grocery request like "1kg tomato" or "2 packs of oreo and ₹10 kurkure" and watch me execute intelligent metrics matching!</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type items to launch instant simulation loop..." onkeypress="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const userInput = document.getElementById('userInput');

        function appendMessage(text, isUser) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `msg ${isUser ? 'user-msg' : 'agent-msg'}`;
            msgDiv.innerHTML = text;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function sendMessage() {
            const query = userInput.value.trim();
            if(!query) return;
            
            appendMessage(query, true);
            userInput.value = '';
            
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'msg agent-msg';
            loadingDiv.innerText = ' Running Instant Playwright Automation Pipeline Engine... Please watch the newly opened browser window...';
            chatBox.appendChild(loadingDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: query })
                });
                const data = await response.json();
                chatBox.removeChild(loadingDiv);
                appendMessage(data.reply, false);
            } catch(e) {
                chatBox.removeChild(loadingDiv);
                appendMessage(' Failure connecting to local backend agent core server thread.', false);
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)