from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Fix the file path to root
        page.goto("file:///app/ipc_training_client.html")

        # Select device
        page.locator("text=RLC-811A (Front Door)").click()

        # Verify the global ROI (Draw a box)
        canvas = page.locator("#annotation-canvas")
        box = canvas.bounding_box()
        page.mouse.move(box["x"] + 50, box["y"] + 50)
        page.mouse.down()
        page.mouse.move(box["x"] + 150, box["y"] + 150)
        page.mouse.up()

        page.wait_for_timeout(500)

        # Ensure Quick Tagging bar is visible
        bar = page.locator("#quick-tagging-bar")
        assert bar.is_visible()

        # Ensure 'Full' button is present and click it
        full_btn = bar.locator("button:has-text('Full')")
        assert full_btn.is_visible()
        full_btn.click()

        # Take a screenshot to verify layout
        page.screenshot(path="classification_ui.png")
        print("Verification complete. Screenshot saved as classification_ui.png")
        browser.close()

if __name__ == "__main__":
    verify()
