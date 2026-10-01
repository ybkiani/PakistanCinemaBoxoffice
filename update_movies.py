import json,re,urllib.request,datetime
from html import unescape
from pathlib import Path

SOURCES=[
 ('ME Cinemas','https://www.mecinemas.com/movies.php','me'),
 ('CineStar','https://cinestar.pk/Browsing/Movies/ComingSoon','vista'),
 ('Universal Cinemas','https://universalcinemas.com/browsing/Movies/ComingSoon','vista'),
 ('Cinepax','https://cinepax.com/Browsing/Movies/NowShowing','vista'),
 ('Showtimes.pk','https://www.showtimes.pk/','generic'),
]
DATA=Path('data/movies.json')

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 PakistanCinemaGuide/2.0 (+GitHub Pages)'} )
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore')
def clean(s): return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>',' ',s))).strip()
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:80]
def movie(title, source, status='now', **kw):
    return {'id':slug(title),'title':title,'status':status,'pakistani':kw.get('language','').lower() in ('urdu','punjabi') or kw.get('pakistani',False),'genre':kw.get('genre','Cinema'),'language':kw.get('language',''),'runtime':kw.get('runtime',''),'releaseDate':kw.get('releaseDate',''),'cast':kw.get('cast',''),'director':kw.get('director',''),'cities':kw.get('cities',[]),'cinemas':kw.get('cinemas',[]),'showtimes':kw.get('showtimes',[]),'poster':kw.get('poster',''),'trailer':kw.get('trailer',''),'description':kw.get('description','Listed by a participating Pakistan cinema source.'),'sourceName':source[0],'sourceUrl':source[1]}

def parse_me(html, source):
    txt=clean(html); out=[]
    # ME's page exposes repeating structured text: Title, runtime, rating, opening, genre/language/cast/director.
    pat=re.compile(r'([A-Za-z0-9][A-Za-z0-9’\'&:!,.\- ]{1,70})\s+Run Time:\s*([0-9]{2}\s*hr\s*[0-9]{2}\s*min).*?([0-9]{2}\s+[A-Za-z]+,\s+20[0-9]{2}).*?Genre:\s*([A-Za-z /-]+).*?Language\s*([A-Za-z ()-]+).*?Cast\s*(.*?)\s*Director\s*(.*?)\s*Opening',re.I)
    today=datetime.date.today()
    for m in pat.finditer(txt):
        title,runtime,date_s,genre,language,cast,director=[x.strip() for x in m.groups()]
        try: d=datetime.datetime.strptime(date_s,'%d %B, %Y').date()
        except: d=today
        status='now' if d<=today else 'soon'
        out.append(movie(title,source,status,runtime=runtime,releaseDate=date_s,genre=genre,language=language,cast=cast,director=director))
    return out

def parse_generic(html, source, default='now'):
    titles=[]
    for tag in ('h2','h3'):
        titles += [clean(x) for x in re.findall(fr'<{tag}[^>]*>(.*?)</{tag}>',html,re.I|re.S)]
    bad={'now showing','coming soon','show times','showtimes','movies'}; out=[]
    for t in titles:
        if 2<len(t)<85 and t.lower() not in bad and not any(x['title'].lower()==t.lower() for x in out): out.append(movie(t,source,default))
    return out

def merge(items):
    d={}
    for m in items:
        k=m['title'].lower().strip()
        if k not in d: d[k]=m
        else:
            a=d[k]
            for f in ('genre','language','runtime','releaseDate','cast','director','poster','trailer','description'):
                if not a.get(f) and m.get(f): a[f]=m[f]
            if m.get('status')=='now': a['status']='now'
    return list(d.values())

try: old=json.loads(DATA.read_text(encoding='utf8'))
except: old={'nowShowing':[],'comingSoon':[],'sources':[]}
items=[]; ok=[]; errors=[]
for name,url,kind in SOURCES:
    src=(name,url)
    try:
        h=get(url)
        parsed=parse_me(h,src) if kind=='me' else parse_generic(h,src,'soon' if 'ComingSoon' in url else 'now')
        if parsed:
            items.extend(parsed); ok.append({'name':name,'url':url,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        else: errors.append(f'{name}: no movie records parsed')
    except Exception as e: errors.append(f'{name}: {type(e).__name__}: {e}')

items=merge(items)
now=[m for m in items if m['status']=='now']
soon=[m for m in items if m['status']=='soon']
# Fail-safe per section. Never destroy the public feed after a parser/site change.
if len(now)<2: now=old.get('nowShowing',[])
if len(soon)<2: soon=old.get('comingSoon',[])
result={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'updateStatus':'ok' if ok else 'fallback','nowShowing':now,'comingSoon':soon,'sources':ok or old.get('sources',[]),'diagnostics':errors}
DATA.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(f'Published {len(now)} now showing + {len(soon)} coming soon from {len(ok)} responding sources')
for e in errors: print('WARN',e)
