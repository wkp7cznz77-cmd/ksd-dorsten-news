import json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 KSD-Dorsten-Ticker/1.0'})
    with urllib.request.urlopen(req,timeout=20) as r:return r.read()

def clean_title(t):
    t=re.sub(r'<[^>]+>',' ',t or '');t=re.sub(r'\s+',' ',t).strip(' -–—|')
    return t

def reject(t):
    s=t.lower();bad=['wetter','regenradar','vorhersage','tagesschau in 100 sekunden','livestream','liveblog','newsticker','ticker','podcast','audio','video','bildergalerie','newsletter','push-nachricht','mehr zum thema','weitere meldungen','aktuelle meldungen','nachrichten im überblick','hier finden sie','lesen sie hier','zum artikel','zur übersicht','aktualisiert','seite wird','programm','sendung','jetzt im live','im tv','mediathek','unsere themen bei instagram','instagram','facebook','whatsapp']
    return len(t)<18 or any(x in s for x in bad)

def words(t):
    stop={'der','die','das','den','dem','des','ein','eine','einer','einem','einen','und','oder','in','im','am','an','auf','aus','bei','mit','für','von','vor','zu','zum','zur','nach','ist','sind','wird','werden','news','pol','re','polizei','recklinghausen'}
    return {w for w in re.findall(r'[a-zäöüß0-9]+',t.lower()) if len(w)>2 and w not in stop}

def similar(a,b):
    wa,wb=words(a),words(b)
    if not wa or not wb:return False
    inter=len(wa&wb)
    # Gleiche Geschichte aus mehreren Quellen erkennen, auch bei abweichenden Überschriften.
    return inter>=3 and (inter/min(len(wa),len(wb))>=0.5 or inter>=5)

def dedupe(items,limit=12):
    out=[];seen=set()
    for t in items:
        t=clean_title(t);key=re.sub(r'[^a-z0-9äöüß]+',' ',t.lower()).strip()
        if reject(t) or not key or key in seen or any(similar(t,x) for x in out):continue
        seen.add(key);out.append(t)
        if len(out)>=limit:break
    return out

def parse_rss_date(item):
    raw=(item.findtext('pubDate') or item.findtext('{http://purl.org/dc/elements/1.1/}date') or '').strip()
    if not raw:return None
    try:
        dt=parsedate_to_datetime(raw)
        if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:return None

def rss_titles(url,limit=12,max_age_hours=30):
    root=ET.fromstring(fetch(url));now=datetime.now(timezone.utc);fresh=[]
    for item in root.findall('.//item'):
        dt=parse_rss_date(item)
        if dt and now-dt>timedelta(hours=max_age_hours):continue
        t=clean_title(item.findtext('title') or '');t=re.sub(r'\s+-\s+[^-]+$','',t).strip()
        if not reject(t):fresh.append((dt or now,t))
    fresh.sort(key=lambda x:x[0],reverse=True)
    return dedupe([t for _,t in fresh],limit)

def parse_api_date(n):
    for k in ('date','breakingNewsDate','firstPublicationDate','lastModified'):
        raw=n.get(k)
        if not raw:continue
        try:return datetime.fromisoformat(str(raw).replace('Z','+00:00')).astimezone(timezone.utc)
        except Exception:pass
    return None

def country_prefix(n):
    text=' '.join(str(n.get(k) or '') for k in ('title','topline','firstSentence')).lower();rules=[('UKRAINE',r'ukrain|kiew|kyiv|selensky'),('RUSSLAND',r'russland|moskau|putin|kreml'),('USA',r'\busa\b|\bus-\b|trump|weißes haus|washington'),('CHINA',r'china|xi jinping|peking'),('ISRAEL',r'israel|netanjahu|jerusalem|gaza'),('IRAN',r'iran|teheran'),('SAUDI-ARABIEN',r'saudi|riad'),('TÜRKEI',r'türkei|türkisch|ankara|erdogan'),('FRANKREICH',r'frankreich|französ|macron|paris'),('DEUTSCHLAND',r'deutschland|bundesregierung|bundestag|berlin'),('POLEN',r'polen|polnisch|warschau|tusk'),('SYRIEN',r'syrien|damaskus'),('EU',r'\beu\b|europäische union|brüssel'),('UN',r'vereinte nationen|un-sicherheitsrat|un-general')];found=[]
    for name,pat in rules:
        if re.search(pat,text) and name not in found:found.append(name)
        if len(found)==2:break
    return '/'.join(found) if found else 'INTERNATIONAL'

def breaking_news(limit=12):
    data=json.loads(fetch('https://www.tagesschau.de/api2u/news/?ressort=ausland&_='+str(int(datetime.now().timestamp()))));now=datetime.now(timezone.utc);c=[]
    for n in data.get('news',[]):
        t=clean_title(n.get('title') or '')
        if reject(t):continue
        dt=parse_api_date(n)
        if dt and now-dt>timedelta(hours=30):continue
        c.append((dt or now,country_prefix(n)+' · '+t))
    c.sort(key=lambda x:x[0],reverse=True);return dedupe([t for _,t in c],limit)

q=urllib.parse.quote('(Dorsten OR Wulfen OR Lembeck OR Rhade OR Hervest OR "Holsterhausen Dorsten") when:1d');local_url=f'https://news.google.com/rss/search?q={q}&hl=de&gl=DE&ceid=DE:de'
try:local=rss_titles(local_url,12,30)
except Exception:local=[]
try:breaking=breaking_news(12)
except Exception:breaking=[]
old={}
try:
    with open('news.json',encoding='utf-8') as f:old=json.load(f)
except Exception:pass
if not local:local=old.get('local',[])
if not breaking:breaking=old.get('breaking',[])
with open('news.json','w',encoding='utf-8') as f:json.dump({'updated':datetime.now(timezone.utc).isoformat(),'local':local,'breaking':breaking},f,ensure_ascii=False,indent=2)
