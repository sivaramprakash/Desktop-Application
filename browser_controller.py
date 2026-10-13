from playwright.sync_api import sync_playwright, Page, Browser
from typing import Optional

class BrowserController:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def _ensure_browser(self):
        if not self.browser:
            self.browser = self.playwright.chromium.launch(headless=False)
        if not self.page or self.page.is_closed():
            self.page = self.browser.new_page()

    def open_website(self, url: str) -> bool:
        try:
            self._ensure_browser()
            if not url.startswith('http'):
                url = 'https://' + url
            self.page.goto(url)
            return True
        except Exception as e:
            print(f"Error opening website: {e}")
            return False

    def search_google(self, query: str) -> bool:
        try:
            self._ensure_browser()
            self.page.goto("https://www.google.com")
            # Wait for search box
            search_box = self.page.locator('textarea[name="q"], input[name="q"]').first
            search_box.fill(query)
            search_box.press('Enter')
            self.page.wait_for_load_state('domcontentloaded')
            return True
        except Exception as e:
            print(f"Error searching Google: {e}")
            return False

    def search_youtube(self, query: str) -> bool:
        try:
            self._ensure_browser()
            self.page.goto(f"https://www.youtube.com/results?search_query={query}")
            self.page.wait_for_load_state('domcontentloaded')
            # Optional: click first video
            # self.page.locator('ytd-video-renderer').first.click()
            return True
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return False

    def click_element(self, selector: str) -> bool:
        try:
            if self.page:
                self.page.click(selector)
                return True
        except Exception as e:
            print(f"Error clicking element: {e}")
        return False

    def type_text(self, selector: str, text: str) -> bool:
        try:
            if self.page:
                self.page.fill(selector, text)
                return True
        except Exception as e:
            print(f"Error typing text: {e}")
        return False
        
    def close_browser(self):
        if self.browser:
            self.browser.close()
            self.browser = None
            self.page = None
            
    def __del__(self):
        if hasattr(self, 'playwright'):
            self.playwright.stop()
