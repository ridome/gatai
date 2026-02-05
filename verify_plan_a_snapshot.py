from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the file
        filepath = os.path.abspath("aibox_demo.html")
        page.goto(f"file://{filepath}")

        # Navigate to Plan A
        page.click("text=PLAN A")

        # Draw ROI
        roi_container = page.locator("#roi-container")
        box = roi_container.bounding_box()
        page.mouse.move(box["x"] + 50, box["y"] + 50)
        page.mouse.down()
        page.mouse.move(box["x"] + 150, box["y"] + 150)
        page.mouse.up()

        # Verify ROI created
        assert page.locator(".roi-box").count() > 0

        # 1. Take snapshot for "Open"
        page.fill("#plana-label-input", "Open")
        page.click("text=截图")

        # Verify image added
        images = page.locator("#plana-images-list .image-thumb")
        assert images.count() == 1
        assert "Open" in images.first.inner_text()

        # 2. Take snapshot for "Closed"
        page.fill("#plana-label-input", "Closed")
        page.click("text=截图")

        # Verify second image added
        assert images.count() == 2
        assert "Closed" in images.nth(1).inner_text()

        # Take screenshot
        output_path = os.path.abspath("/home/jules/verification/plan_a_snapshot_flow.png")
        page.screenshot(path=output_path)
        print(f"Screenshot saved to {output_path}")

        browser.close()

if __name__ == "__main__":
    run()
