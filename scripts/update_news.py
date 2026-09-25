import json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 KSD-Dorsten-Ticker/1.0'})
    with urllib.request.urlopen(req,timeout=20) as r: return r.read()

def rss_titles(url, limit=12):
    root=ET.fromstring(fetch(url)); out=[]
    for item in root.findall('.//item'):
        t=(item.findtext('title') or '').strip()
        t=re.sub(r'\s+-\s+[^-]+$','',t).strip()
        if t and t not in out: out.append(t)
        if len(out)>=limit: break
    return out

def tagesschau(limit=12):
    data=json.loads(fetch('https://www.tagesschau.de/api2u/news/?_='+str(int(datetime.now().timestamp()))))
    out=[]
    for n in data.get('news',[]):
        t=(n.get('title') or '').strip()
        if t and t not in out: out.append(t)
        if len(out)>=limit: break
    return out

q=urllib.parse.quote('Dorsten OR Wulfen OR Lembeck OR Rhade OR Hervest OR Holsterhausen Dorsten')
local_url=f'https://news.google.com/rss/search?q={q}&hl=de&gl=DE&ceid=DE:de'
try: local=rss_titles(local_url,12)
except Exception: local=[]
try: breaking=tagesschau(12)
except Exception: breaking=[]
old={}
try:
    with open('news.json',encoding='utf-8') as f: old=json.load(f)
except Exception: pass
if not local: local=old.get('local',[])
if not breaking: breaking=old.get('breaking',[])
with open('news.json','w',encoding='utf-8') as f:
    json.dump({'updated':datetime.now(timezone.utc).isoformat(),'local':local,'breaking':breaking},f,ensure_ascii=False,indent=2)
