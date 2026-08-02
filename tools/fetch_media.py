import json, os, subprocess, re
from _paths import REPO as CLONE, WORK, STAGE
from concurrent.futures import ThreadPoolExecutor


def slugify(s):
    s=re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
    return s

def fname(rid, title):
    m=re.match(r'([A-Za-z]+)-UAP-(PR|D)0*(\d+[A-Za-z]?)', rid)
    ag,typ,num=m.group(1).lower(),m.group(2).lower(),m.group(3).lower()
    if typ=='pr':
        return f"{ag}-uap-pr{num}.mp4"
    # NASA doc-series: <ag>-uap-d<N>-<short-slug>.mp4
    t=title.split(',',1)[1] if ',' in title else title
    t=t.replace('“','').replace('”','').replace('"','')
    sl='-'.join(slugify(t).split('-')[:6])
    return f"{ag}-uap-d{num}-{sl}.mp4"

recs=json.load(open(os.path.join(WORK,'media_resolved.json')))
recs=[r for r in recs if r['rid']!='NASA-UAP-D024']   # D024 handled by background resume

def get(r):
    dest=os.path.join(STAGE, fname(r['rid'], r['title']))
    exp=r['size']
    for attempt in (1,2):
        have=os.path.getsize(dest) if os.path.exists(dest) else 0
        if have >= exp:
            break
        subprocess.run(["curl","-sL","-C","-","--max-time","800","-o",dest,r['src']],
                       capture_output=True)
        have=os.path.getsize(dest) if os.path.exists(dest) else 0
        if have >= exp: break
    have=os.path.getsize(dest) if os.path.exists(dest) else 0
    magic=b''
    if have>8:
        with open(dest,'rb') as fh: fh.seek(4); magic=fh.read(4)
    ok = have>=exp and magic==b'ftyp'
    return {'rid':r['rid'],'file':os.path.basename(dest),'have':have,'exp':exp,
            'ftyp':magic==b'ftyp','ok':ok}

with ThreadPoolExecutor(max_workers=6) as ex:
    out=list(ex.map(get, recs))

for o in sorted(out, key=lambda x:x['rid']):
    print(f"{'OK ' if o['ok'] else 'PART'} {o['rid']:15s} {o['have']:>10d}/{o['exp']:<10d} ftyp={o['ftyp']} {o['file']}")
json.dump(out, open(os.path.join(WORK,'media_dl.json'),'w'), indent=1)
print(f"\nCOMPLETE {sum(1 for o in out if o['ok'])}/{len(out)}")
