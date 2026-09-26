import json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 KSD-Dorsten-Ticker/1.0'})
    with urllib.request.urlopen(req,timeout=20) as r: return r.read()

def clean_title(t):
    t=re.sub(r'<[^>]+>',' ',t or '')
    t=re.sub(r'\s+',' ',t).strip(' -–—|')
    return t

def reject(t):
    s=t.lower()
    bad=[
        'wetter','regenradar','vorhersage','tagesschau in 100 sekunden','livestream','liveblog',
        'newsticker','ticker','podcast','audio','video','bildergalerie','newsletter','push-nachricht',
        'mehr zum thema','weitere meldungen','aktuelle meldungen','nachrichten im überblick',
        'hier finden sie','lesen sie hier','zum artikel','zur übersicht','aktualisiert','seite wird',
        'programm','sendung','jetzt im live','im tv','mediathek'
    ]
    return len(t)<18 or any(x in s for x in bad)

def dedupe(items, limit=12):
    out=[]; seen=set()
    for t in items:
        t=clean_title(t)
        key=re.sub(r'[^a-z0-9äöüß]+',' ',t.lower()).strip()
        if reject(t) or not key or key in seen: continue
        seen.add(key); out.append(t)
        if len(out)>=limit: break
    return out

def rss_titles(url, limit=12):
    root=ET.fromstring(fetch(url)); titles=[]
    for item in root.findall('.//item'):
        t=clean_title(item.findtext('title') or '')
        # Google News hängt häufig den Quellennamen an; nur die Schlagzeile behalten.
        t=re.sub(r'\s+-\s+[^-]+$','',t).strip()
        titles.append(t)
    return dedupe(titles,limit)

def country_prefix(n):
    text=' '.join(str(n.get(k) or '') for k in ('title','topline','firstSentence')).lower()
    rules=[('UKRAINE',r'ukrain|kiew|kyiv|selensky'),('RUSSLAND',r'russland|moskau|putin|kreml'),('USA',r'\busa\b|\bus-\b|trump|weißes haus|washington'),('CHINA',r'china|xi jinping|peking'),('ISRAEL',r'israel|netanjahu|jerusalem|gaza'),('IRAN',r'iran|teheran'),('SAUDI-ARABIEN',r'saudi|riad'),('TÜRKEI',r'türkei|türkisch|ankara|erdogan'),('FRANKREICH',r'frankreich|französ|macron|paris'),('DEUTSCHLAND',r'deutschland|bundesregierung|bundestag|berlin'),('POLEN',r'polen|polnisch|warschau|tusk'),('SYRIEN',r'syrien|damaskus'),('EU',r'\beu\b|europäische union|brüssel'),('UN',r'vereinte nationen|un-sicherheitsrat|un-general')]
    found=[]
    for name,pat in rules:
        if re.search(pat,text) and name not in found: found.append(name)
        if len(found)==2: break
    return '/'.join(found) if found else 'INTERNATIONAL'

def breaking_news(limit=12):
    data=json.loads(fetch('https://www.tagesschau.de/api2u/news/?ressort=ausland&_='+str(int(datetime.now().timestamp()))))
    candidates=[]
    for n in data.get('news',[]):
        t=clean_title(n.get('title') or '')
        if reject(t): continue
        candidates.append(country_prefix(n)+' · '+t)
    return dedupe(candidates,limit)

q=urllib.parse.quote('Dorsten OR Wulfen OR Lembeck OR Rhade OR Hervest OR "Holsterhausen Dorsten"')
local_url=f'https://news.google.com/rss/search?q={q}&hl=de&gl=DE&ceid=DE:de'
try: local=rss_titles(local_url,12)
except Exception: local=[]
try: breaking=breaking_news(12)
except Exception: breaking=[]
old={}
try:
    with open('news.json',encoding='utf-8') as f: old=json.load(f)
except Exception: pass
if not local: local=old.get('local',[])
if not breaking: breaking=old.get('breaking',[])
with open('news.json','w',encoding='utf-8') as f:
    json.dump({'updated':datetime.now(timezone.utc).isoformat(),'local':local,'breaking':breaking},f,ensure_ascii=False,indent=2)
