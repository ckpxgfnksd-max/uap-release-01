"""Fetch the authoritative record list + DVIDS API key from war.gov.

www.war.gov is behind Akamai, which 403s plain curl AND Playwright's
ctx.request.get(). The ONLY transport that clears it is an in-page fetch()
executed inside a real Chrome context. See fetch_docs.py for the full trap.
"""
import re, json, os
from playwright.sync_api import sync_playwright
from _paths import WORK, CSV

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
CSV_URL = 'https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv'

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    ctx = browser.new_context(user_agent=UA)
    page = ctx.new_page()
    try:
        page.goto('https://www.war.gov/UFO/', wait_until='commit', timeout=120000)
        page.wait_for_timeout(9000)
        html = page.content()
        open(os.path.join(WORK, 'page.html'), 'w').write(html)

        # Key can rotate; re-extract every run, fall back to last known.
        m = re.search(r'DVIDS_API_KEY\s*=\s*"([^"]+)"', html)
        key = m.group(1) if m else 'key-68bb60d16b35e'
        print('DVIDS_KEY=' + key + ('' if m else ' (FALLBACK — not found in page)'))
        open(os.path.join(WORK, 'dvids_key.txt'), 'w').write(key)

        csv = page.evaluate('''async (u) => {
            const r = await fetch(u, {credentials:'include'});
            if (!r.ok) return 'FETCH_FAIL_' + r.status;
            return await r.text();
        }''', CSV_URL)
        if csv.startswith('FETCH_FAIL'):
            print('CSV_ERROR=' + csv); raise SystemExit(1)
        open(CSV, 'w').write(csv)
        print('CSV_BYTES=' + str(len(csv)))
    finally:
        browser.close()
