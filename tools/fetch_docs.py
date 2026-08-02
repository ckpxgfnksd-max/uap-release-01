"""Document fetcher — IN-PAGE fetch() is the ONLY Akamai-clearing transport.

DO NOT switch to ctx.request.get(). Akamai 403s it for EVERY war.gov document,
including ones already successfully mirrored. That drift made DOW-UAP-D092/D093/
D096 look withdrawn for two consecutive runs (2026-07-26, 2026-08-02) when they
were downloadable the whole time. Control test that settled it: three PDFs
already in the mirror also returned 403 on that transport.

Base64 conversion MUST be chunked. String.fromCharCode(...bigArray) overflows the
call stack on large PDFs (D096 is 126 MB) and surfaces as "TypeError: Failed to
fetch", which reads like a network error and is not one.
"""
import json, os, urllib.parse, base64
from playwright.sync_api import sync_playwright
from _paths import REPO, WORK

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')

JS = '''async (u) => {
  try {
    const r = await fetch(u, {credentials:'include'});
    if (!r.ok) return {err:'HTTP_'+r.status};
    const b = new Uint8Array(await r.arrayBuffer());
    let s=''; const CH=0x8000;
    for (let i=0;i<b.length;i+=CH) s += String.fromCharCode.apply(null, b.subarray(i,i+CH));
    return {b64: btoa(s), len: b.length};
  } catch(e) { return {err:'EXC_'+e.message}; }
}'''


def _present(path):
    """True if the file is already mirrored.

    On a GIT_LFS_SKIP_SMUDGE clone the working tree holds ~130-byte LFS POINTERS,
    not payload. A naive size threshold reads those as missing and re-downloads the
    entire corpus. A pointer means the bytes exist on the LFS server — that counts
    as present.
    """
    if not os.path.exists(path):
        return False
    with open(path, 'rb') as fh:
        head = fh.read(64)
    if head.startswith(b'version https://git-lfs'):
        return True
    return os.path.getsize(path) > 1000

MAGIC = (b'%PDF-', b'\x89PNG', b'\xff\xd8\xff', b'II*\x00', b'MM\x00*')

diff = json.load(open(os.path.join(WORK, 'diff.json')))
targets = diff['doc'] + diff.get('img', [])
res = []

with sync_playwright() as p:
    br = p.chromium.launch(channel='chrome', headless=True)
    ctx = br.new_context(user_agent=UA); pg = ctx.new_page()
    pg.goto('https://www.war.gov/UFO/', wait_until='commit', timeout=90000)
    pg.wait_for_timeout(7000)
    for d in targets:
        link = d['link']
        base = urllib.parse.unquote(os.path.basename(link.split('?')[0]))
        dest = os.path.join(REPO, base)
        if _present(dest):
            res.append({'base': base, 'status': 'exists'}); print('exists', base, flush=True); continue
        done = False
        for _ in range(3):
            try:
                r = pg.evaluate(JS, link)
            except Exception as e:
                print(f'  pyexc {str(e)[:60]} {base}', flush=True); continue
            if r.get('err'):
                print(f"  {r['err']} {base}", flush=True); continue
            body = base64.b64decode(r['b64'])
            if any(body.startswith(m) for m in MAGIC):
                open(dest, 'wb').write(body)
                print(f'ok {len(body):>10d} {base}', flush=True)
                res.append({'base': base, 'status': 'ok', 'len': len(body)}); done = True; break
            print(f'  bad-magic {body[:8]!r} {base}', flush=True)
        if not done:
            res.append({'base': base, 'status': 'fail', 'link': link})
    br.close()

json.dump(res, open(os.path.join(WORK, 'docs_result.json'), 'w'), indent=0)
print('DOCS', [(r['base'][:24], r['status']) for r in res], flush=True)
