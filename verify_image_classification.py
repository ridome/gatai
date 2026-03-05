import os
import time
from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Load the HTML file
        file_path = f"file://{os.path.abspath('ipc_training_client.html')}"
        page.goto(file_path)

        # Wait for the UI to load
        page.wait_for_selector('#device-list')

        # Select the first device to activate the workspace
        page.click('#device-list > div:first-child')

        # Wait for the canvas and action bar to be visible
        page.wait_for_selector('#annotation-canvas')
        page.wait_for_selector('#quick-tagging-bar')

        # Draw a bounding box
        canvas = page.locator('#annotation-canvas')
        box = canvas.bounding_box()

        # Simulate drawing a box (mousedown, mousemove, mouseup)
        page.mouse.move(box['x'] + 100, box['y'] + 100)
        page.mouse.down()
        page.mouse.move(box['x'] + 300, box['y'] + 300)
        page.mouse.up()

        # Take a screenshot to verify the UI with the new image
        screenshot_path = "classification_ui_with_image.png"
        page.screenshot(path=screenshot_path, full_page=True)

        print(f"Verification complete. Screenshot saved as {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify()
