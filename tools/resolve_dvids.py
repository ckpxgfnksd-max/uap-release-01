import json, os, subprocess, re
from _paths import WORK
diff=json.load(open(os.path.join(WORK,'diff.json')))
KEY=os.environ.get('DVIDS_KEY') or (open(os.path.join(WORK,'dvids_key.txt')).read().strip() if os.path.exists(os.path.join(WORK,'dvids_key.txt')) else 'key-68bb60d16b35e')
records = diff['video'] + diff['audio']  # both resolve via id=video:<id>
out=[]
for m in records:
    did=m['dvids']
    url=f"https://api.dvidshub.net/asset?api_key={KEY}&id=video:{did}"
    try:
        r=subprocess.run(["curl","-s","--max-time","40",
            "-H","Referer: https://www.war.gov/","-H","Origin: https://www.war.gov",
            "-A","Mozilla/5.0", url], capture_output=True, text=True)
        j=json.loads(r.stdout)
    except Exception as e:
        print("ERR", m['rid'], did, e); out.append({**m,'status':'api_error'}); continue
    files=j.get('results',{}).get('files',[]) if isinstance(j.get('results'),dict) else j.get('results',[])
    # results can be an object with 'files', or the asset itself
    if isinstance(j.get('results'),dict):
        files=j['results'].get('files',[])
    else:
        files=[]
    if not files:
        print("NOFILES", m['rid'], did, str(j)[:200]); out.append({**m,'status':'no_files'}); continue
    # pick canonical original: src matching DOD_<n>/DOD_<n>.mp4 (no -WxH-bitrate)
    canon=None
    for f in files:
        src=f.get('src','')
        if re.search(r'/DOD_(\d+)/DOD_\1\.mp4$', src):
            canon=f; break
    if not canon:
        # fallback: largest .mp4 by size
        mp4s=[f for f in files if f.get('src','').endswith('.mp4')]
        if mp4s: canon=max(mp4s, key=lambda f: int(f.get('size',0) or 0))
    if not canon:
        print("NOMP4", m['rid'], did); out.append({**m,'status':'no_mp4'}); continue
    out.append({'rid':m['rid'],'dvids':did,'title':m['title'],'src':canon['src'],'size':int(canon.get('size',0) or 0),'status':'resolved'})
    print(f"resolved {m['rid']:16s} {int(canon.get('size',0) or 0)/1e6:8.1f}MB  {canon['src'][-55:]}")
json.dump([o for o in out if o.get('status')=='resolved'], open(os.path.join(WORK,'media_resolved.json'),'w'), indent=1)
json.dump(out, open(os.path.join(WORK,'media_resolve_all.json'),'w'), indent=1)
res=[o for o in out if o.get('status')=='resolved']
print(f"\nRESOLVED {len(res)}/{len(records)}  total {sum(o['size'] for o in res)/1e9:.2f} GB")
for o in out:
    if o.get('status')!='resolved': print("  UNRESOLVED:", o['rid'], o['dvids'], o.get('status'))
