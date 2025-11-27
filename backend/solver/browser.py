"""
Browser management using Playwright
Handles JavaScript-rendered pages, dynamic content, and complex interactions
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages headless browser operations using Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context = None
    
    async def start(self):
        """Initialize browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    '--disable-background-networking',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-breakpad',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-features=TranslateUI,BlinkGenPropertyTrees',
                    '--disable-ipc-flooding-protection',
                    '--disable-renderer-backgrounding',
                    '--enable-features=NetworkService,NetworkServiceInProcess',
                    '--force-color-profile=srgb',
                    '--hide-scrollbars',
                    '--metrics-recording-only',
                    '--mute-audio',
                    '--no-first-run',
                    '--single-process'
                ]
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = await self.context.new_page()
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    async def load_page(self, url: str, wait_for: str = "networkidle") -> Dict[str, Any]:
        """
        Load page and wait for JavaScript execution
        
        Args:
            url: URL to load
            wait_for: Wait strategy (networkidle, load, domcontentloaded)
        
        Returns:
            Dictionary with page content and metadata
        """
        try:
            logger.info(f"Loading page: {url}")
            
            # Navigate to page
            response = await self.page.goto(url, wait_until=wait_for, timeout=30000)
            
            # Wait for additional JS execution
            await asyncio.sleep(2)
            
            # Wait for common dynamic content indicators
            try:
                await self.page.wait_for_selector('body', timeout=5000)
            except PlaywrightTimeout:
                logger.warning("Timeout waiting for body element")
            
            # Execute JavaScript to handle base64 decoding and dynamic content
            await self.page.evaluate("""
                () => {
                    // Trigger any lazy-loaded content
                    window.scrollTo(0, document.body.scrollHeight);
                    window.scrollTo(0, 0);
                }
            """)
            
            await asyncio.sleep(1)
            
            # Get page content
            html_content = await self.page.content()
            
            # Get all text content
            text_content = await self.page.evaluate("() => document.body.innerText")
            
            # Get all script contents (for embedded data)
            scripts = await self.page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('script'))
                        .map(s => s.textContent)
                        .filter(t => t && t.trim().length > 0);
                }
            """)
            
            # Check for iframes
            frames = self.page.frames
            iframe_contents = []
            for frame in frames[1:]:  # Skip main frame
                try:
                    iframe_html = await frame.content()
                    iframe_contents.append(iframe_html)
                except Exception as e:
                    logger.warning(f"Could not access iframe: {e}")
            
            # Extract all links (potential submit URLs, data URLs)
            links = await self.page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a, link, form'))
                        .map(el => ({
                            tag: el.tagName,
                            // Use getAttribute to preserve data: URLs exactly as written
                            href: el.getAttribute('href') || el.getAttribute('action') || el.href || el.action || '',
                            text: el.textContent?.trim() || '',
                            method: el.method || '',
                            id: el.id || '',
                            className: el.className || '',
                            download: el.download || ''
                        }))
                        .filter(item => item.href);
                }
            """)
            
            # Extract all data attributes
            data_attrs = await self.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('[data-url], [data-submit], [data-api], [data-file]');
                    return Array.from(elements).map(el => ({
                        url: el.dataset.url || '',
                        submit: el.dataset.submit || '',
                        api: el.dataset.api || '',
                        file: el.dataset.file || '',
                        element: el.tagName
                    }));
                }
            """)
            
            # Extract forms
            forms = await self.page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('form')).map(form => ({
                        action: form.action,
                        method: form.method,
                        id: form.id,
                        fields: Array.from(form.elements).map(el => ({
                            name: el.name,
                            type: el.type,
                            id: el.id
                        }))
                    }));
                }
            """)
            
            # Extract tables
            tables = await self.page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('table')).map(table => {
                        const rows = Array.from(table.rows);
                        return rows.map(row => 
                            Array.from(row.cells).map(cell => cell.textContent?.trim() || '')
                        );
                    });
                }
            """)
            
            # Extract images (including base64)
            images = await self.page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('img')).map(img => ({
                        src: img.src,
                        alt: img.alt,
                        isBase64: img.src.startsWith('data:')
                    }));
                }
            """)
            
            logger.info(f"Page loaded successfully. Found {len(scripts)} scripts, {len(forms)} forms, {len(tables)} tables, {len(links)} links")
            
            # Log data: URLs for debugging
            data_urls = [link for link in links if link.get('href', '').startswith('data:')]
            if data_urls:
                logger.info(f"Found {len(data_urls)} data: URLs")
            
            return {
                "url": url,
                "status": response.status if response else 200,
                "html": html_content,
                "text": text_content,
                "scripts": scripts,
                "links": links,
                "data_attrs": data_attrs,
                "forms": forms,
                "tables": tables,
                "images": images,
                "iframes": iframe_contents
            }
        
        except PlaywrightTimeout as e:
            logger.error(f"Timeout loading page {url}: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            raise
    
    async def click_and_wait(self, selector: str, wait_for: str = "networkidle"):
        """Click element and wait for navigation"""
        try:
            await self.page.click(selector)
            await self.page.wait_for_load_state(wait_for, timeout=10000)
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {e}")
            raise
    
    async def fill_form(self, selector: str, value: str):
        """Fill form field"""
        try:
            await self.page.fill(selector, value)
        except Exception as e:
            logger.error(f"Error filling form {selector}: {e}")
            raise
    
    async def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get element attribute value"""
        try:
            return await self.page.get_attribute(selector, attribute)
        except Exception as e:
            logger.warning(f"Could not get attribute {attribute} from {selector}: {e}")
            return None
    
    async def evaluate_js(self, script: str) -> Any:
        """Execute JavaScript in page context"""
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            logger.error(f"Error evaluating JavaScript: {e}")
            return None
    
    async def screenshot(self, path: Optional[str] = None) -> bytes:
        """Take screenshot"""
        try:
            return await self.page.screenshot(path=path, full_page=True)
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return b""
    
    async def close(self):
        """Close browser"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
