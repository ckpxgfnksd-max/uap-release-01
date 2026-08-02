import csv, os, re, json, urllib.parse, glob
from _paths import REPO as CLONE, WORK, CSV
rows=list(csv.DictReader(open(CSV)))

# mirror content files (exclude meta)
EXCL={'.gitattributes','.gitignore','README.md'}
mirror=set()
for f in os.listdir(CLONE):
    if f in EXCL or f.startswith('.git'): continue
    if os.path.isfile(os.path.join(CLONE,f)): mirror.add(f)

def slug(s):
    s=re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-'); return s

def rid_from_title(t):
    m=re.match(r'\s*([A-Za-z]+-UAP-(?:PR|D)?0*\d+[A-Za-z]?)', t)
    return m.group(1) if m else None

def media_fname_prefix(rid):
    # returns (glob_pattern_list) for matching DVIDS records by record-id prefix
    mm=re.match(r'([A-Za-z]+)-UAP-(PR|D)0*(\d+[A-Za-z]?)', rid)
    if not mm: return None
    ag,typ,num=mm.group(1).lower(),mm.group(2).lower(),mm.group(3).lower()
    if typ=='pr':
        return [f"{ag}-uap-pr{num}.*"]
    else:
        return [f"{ag}-uap-d{num}.*", f"{ag}-uap-d{num}-*"]

diff={'doc':[],'img':[],'video':[],'audio':[],'unmatched_media':[]}
docs_present=0; media_present=0

for r in rows:
    typ=r.get('Type','').strip()
    title=r.get('Title','').strip()
    link=r.get('PDF | Image Link','').strip()
    dvids=r.get('DVIDS Video ID','').strip()
    rel=r.get('Release Date','').strip()
    rid=rid_from_title(title)
    if typ in ('PDF','IMG'):
        if not link:
            continue
        base=urllib.parse.unquote(os.path.basename(link.split('?')[0]))
        if base in mirror:
            docs_present+=1
        else:
            (diff['img'] if typ=='IMG' else diff['doc']).append({'rid':rid,'title':title,'link':link,'base':base,'rel':rel})
    elif typ in ('VID','AUD'):
        if not dvids:
            diff['unmatched_media'].append({'rid':rid,'title':title,'reason':'no_dvids_id','rel':rel})
            continue
        pats=media_fname_prefix(rid) if rid else None
        found=False
        if pats:
            for p in pats:
                if glob.glob(os.path.join(CLONE,p)):
                    found=True; break
        if found:
            media_present+=1
        else:
            (diff['audio'] if typ=='AUD' else diff['video']).append({'rid':rid,'title':title,'dvids':dvids,'rel':rel})

# missing-from-warGov: mirror files not matched to any CSV record
# build set of expected basenames (docs) + matched media files
expected_docs=set()
for r in rows:
    if r.get('Type','').strip() in ('PDF','IMG'):
        link=r.get('PDF | Image Link','').strip()
        if link: expected_docs.add(urllib.parse.unquote(os.path.basename(link.split('?')[0])))
# media: collect all rids
media_rids=[rid_from_title(r['Title']) for r in rows if r.get('Type','').strip() in ('VID','AUD')]
media_patterns=[]
for rid in media_rids:
    if rid:
        p=media_fname_prefix(rid)
        if p: media_patterns+=p
matched_media=set()
for p in media_patterns:
    for fp in glob.glob(os.path.join(CLONE,p)):
        matched_media.add(os.path.basename(fp))

missing=[]
for f in sorted(mirror):
    if f in expected_docs: continue
    if f in matched_media: continue
    if f.endswith('.zip'): continue  # bundles
    missing.append(f)

diff['missing']=missing
json.dump(diff, open(os.path.join(WORK,'diff.json'),'w'), indent=1)
print(f"records: {len(rows)}  mirror files: {len(mirror)}")
print(f"docs present: {docs_present}  NEW docs: {len(diff['doc'])}  NEW img: {len(diff['img'])}")
print(f"media present: {media_present}  NEW video: {len(diff['video'])}  NEW audio: {len(diff['audio'])}")
print(f"unmatched media (no dvids): {len(diff['unmatched_media'])}")
print(f"mirror files NOT matched to any record: {len(missing)}")
for m in missing[:40]: print('   unmatched-in-mirror:', m)
print('---NEW docs---')
for d in diff['doc'][:30]: print('  ',d['base'])
print('---NEW video---')
for d in diff['video'][:30]: print('  ',d['rid'], d['dvids'], d['title'][:50])
print('---NEW audio---')
for d in diff['audio'][:30]: print('  ',d['rid'], d['dvids'], d['title'][:50])
