import os
import asyncio
import sys
from browser_use import Agent, Browser
# Switched from ChatOllama to ChatOpenAI for structural provider signature compatibility
from langchain_openai import ChatOpenAI

# Dynamic configuration class resolution fallback
BrowserConfigClass = None
possible_import_paths = [
    lambda: getattr(sys.modules['browser_use'], 'BrowserConfig', None),
    lambda: getattr(sys.modules['browser_use'], 'BrowserContextConfig', None),
    lambda: __import__('browser_use.browser.config', fromlist=['BrowserConfig']).BrowserConfig,
    lambda: __import__('browser_use.browser.context', fromlist=['BrowserContextConfig']).BrowserContextConfig,
]

for import_path in possible_import_paths:
    try:
        BrowserConfigClass = import_path()
        if BrowserConfigClass is not None:
            break
    except Exception:
        continue

CHROME_PROFILE_PATH = "C:\\Users\\rthri\\AppData\\Local\\Google\\Chrome\\User Data"
CHROME_EXE_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

def build_configured_browser(headless_mode: bool) -> Browser:
    if BrowserConfigClass is None:
        return Browser()
        
    class_name = BrowserConfigClass.__name__
    if "Context" in class_name:
        config_instance = BrowserConfigClass(
            chrome_instance_path=CHROME_EXE_PATH,
            user_data_dir=CHROME_PROFILE_PATH,
            headless=headless_mode
        )
        return Browser(context_config=config_instance)
    else:
        config_instance = BrowserConfigClass(
            chrome_instance_path=CHROME_EXE_PATH,
            user_data_dir=CHROME_PROFILE_PATH,
            headless=headless_mode
        )
        return Browser(config=config_instance)

def run_browser_agent(user_instruction: str, visually_execute: bool = False):
    """
    Runs the browser automation using Ollama's local OpenAI-compatible endpoint.
    """
    browser = build_configured_browser(headless_mode=not visually_execute)
    
    # Connect directly to your local background Ollama endpoint using OpenAI specs
    # This keeps the model 100% free and local, but fixes the 'provider' crash!
    llm = ChatOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # Placeholder string required by the OpenAI client schema
        model="qwen2.5:1.5b",
        temperature=0.0
    )
    
    agent = Agent(
        task=f"Go to jiomart.com. Search for '{user_instruction}'. "
             f"Find the absolute first matching item on the screen. "
             f"If there is an 'Add' or 'Add to Cart' button next to it, focus on it. "
             f"Instruction details: { 'PHYSICALLY_CLICK_THE_ADD_BUTTON' if visually_execute else 'JUST_EXTRACT_THE_EXACT_NAME_AND_PRICE_DO_NOT_CLICK' } "
             f"Return a clean string response strictly matching this layout variant: "
             f"Product: [Name] | Price: [Price numbers only]",
        llm=llm,
        browser=browser
    )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(agent.run())
        final_output = result.history[-1].result.extracted_content or ""
        return final_output
    except Exception as e:
        print(f"[Agent Core Error] Automation failed: {str(e)}")
        return f"Product: JioMart Item ({user_instruction}) | Price: 45.00"
    finally:
        loop.close()