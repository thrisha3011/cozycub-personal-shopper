from playwright.sync_api import sync_playwright
import time

def execute_browser_add_to_cart(url: str):
    """Launches your local desktop Chrome profile on screen and adds the item to the cart."""
    print(f"\n[Playwright Core] Launching live visual Chrome driver session for: {url}")
    
    # Secure mapping path targeting your Windows Google Chrome profile cache folder
    user_data_dir = "C:\\Users\\rthri\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    
    with sync_playwright() as p:
        try:
            browser_context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                channel="chrome",
                headless=False, # Must be False so you can watch your agent work!
                args=["--start-maximized"]
            )
            page = browser_context.new_page()
            page.goto(url, timeout=45000, wait_until="domcontentloaded")
            time.sleep(5) # Let elements settle down completely
            
            # Action button target elements signature mapping array
            cart_selectors = [
                "button:has-text('Add to Cart')", "button:has-text('ADD TO CART')",
                "button.add-to-cart", "button:has-text('Add')", "span:has-text('Add')"
            ]
            
            clicked = False
            for selector in cart_selectors:
                locator = page.locator(selector).first
                if locator.is_visible() and locator.is_enabled():
                    locator.scroll_into_view_if_needed()
                    time.sleep(1)
                    locator.click()
                    print(f"[Playwright Core] Successfully clicked action target selector: '{selector}'")
                    clicked = True
                    time.sleep(4) # Let you verify visual feedback on screen
                    break
                    
            if not clicked:
                print("[Playwright Warning] Add button obscured. Leaving viewport open briefly.")
                time.sleep(4)
                
            browser_context.close()
        except Exception as e:
            print(f"[Playwright Crash] Automation pipeline broken: {str(e)}")