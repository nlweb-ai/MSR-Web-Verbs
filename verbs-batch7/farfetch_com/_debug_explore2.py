import os, sys, shutil
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws

port = get_free_port()
profile_dir = get_temp_profile_dir("farfetch_debug2")
chrome_proc = launch_chrome(profile_dir, port)
ws_url = wait_for_cdp_ws(port)

with sync_playwright() as pw:
    browser = pw.chromium.connect_over_cdp(ws_url)
    ctx = browser.contexts[0]
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    try:
        page.goto("https://www.farfetch.com/shopping/women/search/items.aspx?q=Gucci+bags", wait_until="domcontentloaded")
        page.wait_for_timeout(6000)
        
        results = page.evaluate(r"""(max) => {
            // Try product card selectors
            const selectors = [
                '[data-testid="productCard"]', '[data-component="ProductCard"]',
                'article', '[class*="ProductCard"]', 'li[class*="product"]',
                '[itemtype*="Product"]', '[data-component="productCard"]'
            ];
            for (const sel of selectors) {
                const els = document.querySelectorAll(sel);
                if (els.length >= 3) {
                    return {selector: sel, count: els.length, samples: Array.from(els).slice(0, 2).map(el => ({
                        html: el.outerHTML.slice(0, 500),
                        text: el.innerText.slice(0, 200)
                    }))};
                }
            }
            
            // Fallback: look for product links
            const links = document.querySelectorAll('a[href*="/shopping/"]');
            return {selector: 'product links', count: links.length, samples: Array.from(links).slice(0, 5).map(a => ({
                href: a.href, text: a.textContent.trim().slice(0, 100)
            }))};
        }""", 5)
        
        print(f"Selector: {results['selector']}, Count: {results['count']}")
        for i, s in enumerate(results.get('samples', [])):
            print(f"\n  Sample {i+1}:")
            for k, v in s.items():
                print(f"    {k}: {str(v)[:400]}")
    finally:
        browser.close()
        chrome_proc.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)
