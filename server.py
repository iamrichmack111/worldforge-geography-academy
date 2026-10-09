"""WorldForge Classroom: local SQLite-backed geography assignments and accounts."""
from __future__ import annotations
import hashlib, hmac, json, os, secrets, sqlite3, threading
from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('WORLDFORGE_DB', str(ROOT / 'classroom.sqlite3')))
LOCK = threading.RLock()
SESSION_HOURS = 168
MAX_BODY = 16000
QUIZ_BANK = [
 ('landforms','Which landform is generally low ground between higher slopes?', ['Plateau','Valley','Ridge','Summit'],1,'A valley lies between higher areas and often carries a river.'),
 ('landforms','What does a ridge commonly separate?', ['Two drainage directions','Two time zones','Two continents','Two oceans'],0,'A ridge can act as a drainage divide.'),
 ('topography','Closely spaced contour lines indicate which type of slope?', ['Flat','Steep','Underwater','Unknown'],1,'Elevation changes rapidly over a short horizontal distance.'),
 ('topography','Contour lines connect locations with the same what?', ['Population','Elevation','Rainfall','Latitude'],1,'Each individual contour follows a constant elevation.'),
 ('watersheds','What primarily causes surface runoff to flow downhill?', ['Gravity','Longitude','Moonlight','Magnetism'],0,'Gravity pulls water from higher toward lower elevations.'),
 ('watersheds','A watershed is an area of land that drains toward a shared what?', ['Language','Outlet','Biome','Temperature'],1,'Its water flows toward a common outlet.'),
 ('climate','Climate describes which of the following?', ['An afternoon storm','Long-term weather patterns','A single cold day','One lightning strike'],1,'Climate reflects weather patterns over many years.'),
 ('climate','Which is usually colder when other factors are similar?', ['High elevation','Low elevation','Sea-level coast','Valley floor'],0,'Air temperature generally decreases with elevation.'),
 ('latitude','Which influences average solar energy by changing the sun angle?', ['Latitude','Soil color alone','Road width','City name'],0,'Latitude affects the angle and duration of sunlight.'),
 ('latitude','Which factor can also modify regional temperatures?', ['Ocean currents','Map borders','Country names','Road signs'],0,'Ocean currents redistribute heat.'),
 ('biomes','Which pair strongly influences the distribution of terrestrial biomes?', ['Temperature and precipitation','Longitude and time zone','Population and language','Roads and railways'],0,'Long-term warmth and moisture shape broad vegetation zones.'),
 ('biomes','A desert is primarily defined by its what?', ['Lack of mountains','Low precipitation','High temperatures always','Distance from oceans'],1,'Cold deserts exist; low precipitation is key.'),
 ('maps','Which are the four cardinal directions?', ['North east south west','Up down left right','NE SE SW NW','Tropic polar temperate arid'],0,'North, east, south and west are the cardinal directions.'),
 ('maps','Why must you know a map scale to estimate ground distance?', ['It relates map length to real distance','It sets the elevation','It predicts the weather','It shows political borders'],0,'Scale describes the relationship between distances on a map and on the ground.'),
 ('tectonics','Converging tectonic plates can create which feature?', ['Mountain ranges','Time zones','Map scales','Watershed names'],0,'Collision and uplift can form mountain belts.'),
 ('tectonics','What commonly happens at plate boundaries?', ['Earthquakes','Seasons stop','Oceans freeze','Longitude changes'],0,'Many earthquakes occur where tectonic plates interact.'),
]

QUIZ_BANK.extend([
    ('landforms', 'What is a plateau?', ['An elevated relatively flat region', 'A deep ocean trench', 'A glacier tongue', 'A river mouth'], 0, 'A plateau is high ground with a relatively level surface.'),
    ('landforms', 'What is a delta?', ['A mountain pass', 'Sediment deposited near a river mouth', 'A volcano crater', 'A tectonic fault'], 1, 'Deltas develop when rivers deposit sediment near their mouths.'),
    ('landforms', 'What is a peninsula?', ['Land surrounded by water on three sides', 'An underwater volcano', 'An enclosed lake', 'A high ridge'], 0, 'Peninsulas project into water and remain connected to larger land.'),
])
QUIZ_BANK.extend([
    ('topography', 'What do index contours usually show?', ['Major labeled elevations', 'Sea currents', 'Political borders', 'Road speeds'], 0, 'Index contours are emphasized and frequently labeled with elevation.'),
    ('topography', 'What is the contour interval?', ['Difference in elevation between neighboring contour lines', 'Width of a river', 'Distance to the equator', 'Map publication year'], 0, 'Contour intervals express fixed vertical elevation differences.'),
    ('topography', 'A contour crossing a stream typically forms a V pointing which way?', ['Downstream', 'Upstream', 'East', 'Toward sea level always'], 1, 'Contours form V shapes pointing upstream in stream valleys.'),
])
QUIZ_BANK.extend([
    ('watersheds', 'What separates adjacent drainage basins?', ['A drainage divide', 'A time zone', 'A county line', 'A latitude line'], 0, 'Higher terrain often forms the divide between drainage basins.'),
    ('watersheds', 'Which surfaces often increase stormwater runoff?', ['Forests', 'Permeable soil', 'Pavement', 'Wetlands'], 2, 'Impervious pavement prevents infiltration and increases runoff.'),
    ('watersheds', 'What is a tributary?', ['A stream joining a larger river', 'A mountain summit', 'A tidal wave', 'An ocean current'], 0, 'Tributaries feed water into larger streams or rivers.'),
])
QUIZ_BANK.extend([
    ('climate', 'What is the difference between weather and climate?', ['Climate is one day', 'Weather is short term, climate is long term', 'They are identical', 'Weather only occurs on coasts'], 1, 'Weather describes short-term conditions; climate describes long-term patterns.'),
    ('climate', 'Which climate pattern is often seen on a leeward mountain side?', ['Rain shadow', 'Permanent monsoon', 'Polar night', 'Tidal surge'], 0, 'Descending air often warms and dries on the leeward side, producing a rain shadow.'),
    ('climate', 'What generally moderates coastal temperatures?', ['Nearby ocean water', 'Longitude alone', 'Political borders', 'Mountain height alone'], 0, 'The ocean heats and cools slowly, reducing temperature extremes nearby.'),
])
QUIZ_BANK.extend([
    ('latitude', 'What is the latitude of the equator?', ['0°', '90° N', '180°', '45° S'], 0, 'The equator is 0 degrees latitude.'),
    ('latitude', 'Latitude lines run generally in which direction?', ['North–south', 'East–west', 'Vertically on the globe', 'Only across oceans'], 1, 'Parallels of latitude encircle Earth in an east-west direction.'),
    ('latitude', 'Which location is closer to the North Pole?', ['20° N', '75° N', '10° S', '0°'], 1, '75 degrees north is closer to the North Pole at 90 degrees north.'),
])
QUIZ_BANK.extend([
    ('biomes', 'What biome often has permanently frozen subsoil?', ['Tundra', 'Tropical rainforest', 'Savanna', 'Mangrove'], 0, 'Permafrost is common in tundra landscapes.'),
    ('biomes', 'What is a savanna?', ['A grassland with scattered trees', 'An ice sheet', 'A deep lake', 'A coral reef'], 0, 'Savannas are tropical or subtropical grasslands with scattered trees.'),
    ('biomes', 'Which biome usually receives very high rainfall year-round?', ['Hot desert', 'Tropical rainforest', 'Arctic tundra', 'Temperate grassland'], 1, 'Tropical rainforests generally have warm temperatures and abundant precipitation.'),
])
QUIZ_BANK.extend([
    ('maps', 'What is a map legend?', ['An explanation of map symbols', 'A map projection', 'A road', 'A compass direction'], 0, 'Legends explain colors and symbols on a map.'),
    ('maps', 'Which line measures positions east or west of the prime meridian?', ['Latitude', 'Longitude', 'Contour', 'Isotherm'], 1, 'Longitude measures angular distance east or west of the prime meridian.'),
    ('maps', 'What is a map projection?', ['A way to show Earth’s curved surface on a flat map', 'A way to calculate age', 'A weather forecast', 'A mountain height'], 0, 'Projections transfer a curved surface to a plane and introduce distortions.'),
])
QUIZ_BANK.extend([
    ('tectonics', 'At a divergent plate boundary, plates generally do what?', ['Move apart', 'Move toward each other', 'Stop moving', 'Always overlap'], 0, 'Divergent boundaries form where plates spread apart.'),
    ('tectonics', 'What is subduction?', ['One plate descends beneath another', 'A river dries out', 'A glacier melts', 'A continent moves north only'], 0, 'Subduction happens where one tectonic plate sinks beneath another.'),
    ('tectonics', 'The Mid-Atlantic Ridge is mainly associated with which process?', ['Seafloor spreading', 'Desertification', 'Glacial erosion', 'River deposition'], 0, 'New oceanic crust forms along the divergent Mid-Atlantic Ridge.'),
])
QUIZ_BANK.extend([
    ('africa', 'Which major desert spans much of northern Africa?', ['Sahara', 'Gobi', 'Atacama', 'Mojave'], 0, 'The Sahara is a vast hot desert across North Africa.'),
    ('africa', 'Which river flows north toward the Mediterranean Sea?', ['Nile', 'Congo', 'Zambezi', 'Niger'], 0, 'The Nile flows generally north through northeastern Africa.'),
    ('africa', 'Which African mountain is the continent’s highest?', ['Kilimanjaro', 'Atlas', 'Table Mountain', 'Mount Kenya'], 0, 'Kilimanjaro is Africa’s highest mountain.'),
    ('africa', 'The Great Rift Valley is connected mainly to what?', ['Tectonic extension', 'Glacial carving alone', 'Meteor impacts', 'Ocean tides'], 0, 'The East African Rift forms as parts of the lithosphere pull apart.'),
    ('africa', 'Madagascar lies off which African coast?', ['Southeast', 'Northwest', 'North', 'West'], 0, 'Madagascar lies in the Indian Ocean off southeastern Africa.'),
])
QUIZ_BANK.extend([
    ('antarctica', 'Which pole lies on Antarctica?', ['South Pole', 'North Pole', 'Magnetic equator', 'Prime Meridian only'], 0, 'The geographic South Pole is located in Antarctica.'),
    ('antarctica', 'What covers most of Antarctica?', ['An ice sheet', 'Tropical forest', 'Savanna', 'Sand dunes'], 0, 'Most of Antarctica is covered by a thick continental ice sheet.'),
    ('antarctica', 'Which ocean surrounds Antarctica?', ['Southern Ocean', 'Arctic Ocean', 'Indian Ocean only', 'Atlantic Ocean only'], 0, 'The Southern Ocean encircles Antarctica.'),
    ('antarctica', 'Antarctica is classified as which kind of desert?', ['Polar desert', 'Tropical desert', 'Monsoon desert', 'Coastal rainforest'], 0, 'Antarctica receives little precipitation, so it is a polar desert.'),
    ('antarctica', 'What is an ice shelf?', ['Floating glacier ice extending from land', 'A mountain peak', 'A frozen river only', 'A lava plateau'], 0, 'Ice shelves are floating extensions of land-based ice.'),
])
QUIZ_BANK.extend([
    ('asia', 'Which mountain range includes Mount Everest?', ['Himalayas', 'Andes', 'Alps', 'Rockies'], 0, 'Mount Everest lies in the Himalayas.'),
    ('asia', 'Which continent is largest by land area?', ['Asia', 'Europe', 'Australia', 'Antarctica'], 0, 'Asia is the largest continent by land area.'),
    ('asia', 'Which plateau is often called the Roof of the World?', ['Tibetan Plateau', 'Colorado Plateau', 'Deccan Plateau', 'Altiplano'], 0, 'The Tibetan Plateau is exceptionally high and extensive.'),
    ('asia', 'Which desert spans parts of Mongolia and China?', ['Gobi', 'Sahara', 'Namib', 'Sonoran'], 0, 'The Gobi is a major cold desert in East Asia.'),
    ('asia', 'The Mekong River flows through which region?', ['Southeast Asia', 'Northern Europe', 'South America', 'East Africa'], 0, 'The Mekong crosses mainland Southeast Asia.'),
])
QUIZ_BANK.extend([
    ('europe', 'Which mountain range separates Spain and France?', ['Pyrenees', 'Andes', 'Urals', 'Atlas'], 0, 'The Pyrenees form a natural boundary between Spain and France.'),
    ('europe', 'Which sea lies south of much of Europe?', ['Mediterranean Sea', 'Caribbean Sea', 'Red Sea', 'Bering Sea'], 0, 'The Mediterranean borders southern Europe.'),
    ('europe', 'Which river passes through Vienna and Budapest?', ['Danube', 'Nile', 'Amazon', 'Mississippi'], 0, 'The Danube flows through several Central and Eastern European cities.'),
    ('europe', 'Which mountain range runs through Switzerland and Austria?', ['Alps', 'Himalayas', 'Drakensberg', 'Appalachians'], 0, 'The Alps stretch across several European countries.'),
    ('europe', 'Scandinavia is located in which part of Europe?', ['Northern', 'Southern', 'Western only', 'Southeastern'], 0, 'Scandinavia is part of Northern Europe.'),
])
QUIZ_BANK.extend([
    ('north_america', 'Which mountain range extends through western North America?', ['Rocky Mountains', 'Himalayas', 'Alps', 'Atlas'], 0, 'The Rockies are a major western North American mountain system.'),
    ('north_america', 'Which system contains Lakes Superior, Michigan, Huron, Erie and Ontario?', ['Great Lakes', 'Caspian Basin', 'African Rift Lakes', 'Andean Lakes'], 0, 'These five lakes are called the Great Lakes.'),
    ('north_america', 'Which river empties into the Gulf of Mexico?', ['Mississippi', 'Danube', 'Yangtze', 'Rhine'], 0, 'The Mississippi River flows south to the Gulf of Mexico.'),
    ('north_america', 'Which country occupies most of northern North America?', ['Canada', 'Brazil', 'Egypt', 'Norway'], 0, 'Canada spans a large part of northern North America.'),
    ('north_america', 'Which landform is carved by the Colorado River in Arizona?', ['Grand Canyon', 'Great Rift Valley', 'Loire Valley', 'Gobi Basin'], 0, 'The Colorado River carved the Grand Canyon over geologic time.'),
])
QUIZ_BANK.extend([
    ('south_america', 'Which mountain range follows western South America?', ['Andes', 'Rockies', 'Alps', 'Urals'], 0, 'The Andes run along the western edge of South America.'),
    ('south_america', 'Which major river drains much of northern South America?', ['Amazon', 'Nile', 'Danube', 'Volga'], 0, 'The Amazon River and its tributaries drain a vast basin.'),
    ('south_america', 'Which biome covers much of the Amazon Basin?', ['Tropical rainforest', 'Tundra', 'Steppe', 'Ice cap'], 0, 'Much of the Amazon Basin is covered by tropical rainforest.'),
    ('south_america', 'Which desert lies along the Pacific coast of Chile?', ['Atacama', 'Sahara', 'Kalahari', 'Gobi'], 0, 'The Atacama is one of the driest nonpolar deserts.'),
    ('south_america', 'Patagonia is mainly in which part of South America?', ['Southern', 'Northern', 'Equatorial', 'Western Caribbean'], 0, 'Patagonia occupies the southern parts of Argentina and Chile.'),
])
QUIZ_BANK.extend([
    ('australia_oceania', 'Which continent is the smallest by land area in the seven-continent model?', ['Australia', 'Asia', 'Africa', 'Europe'], 0, 'Australia is the smallest continent by land area.'),
    ('australia_oceania', 'Which reef system lies off northeastern Australia?', ['Great Barrier Reef', 'Mesoamerican Reef', 'Red Sea Reef', 'Florida Reef'], 0, 'The Great Barrier Reef stretches along Queensland’s coast.'),
    ('australia_oceania', 'New Zealand lies in which ocean?', ['Pacific Ocean', 'Arctic Ocean', 'Atlantic Ocean', 'Southern Ocean only'], 0, 'New Zealand is in the southwestern Pacific Ocean.'),
    ('australia_oceania', 'What is the Outback?', ['A broad remote interior region of Australia', 'A coral lagoon', 'An Antarctic glacier', 'A European forest'], 0, 'The Outback refers to remote inland areas of Australia.'),
    ('australia_oceania', 'Many Pacific islands formed through which process?', ['Volcanism', 'Continental glaciation only', 'River deltas only', 'Wind erosion only'], 0, 'Many islands in Oceania have volcanic origins.'),
])


DEFAULT_ASSIGNMENTS = [
('Mapping mountain ranges','Explore the elevation layer. Identify a high ridge and a neighboring valley. Explain how the elevation changes and what that means for slope.','elevation',7),
('Watersheds and rivers','Use the terrain and cross-section tool. Describe where runoff would likely flow and why water does not travel uphill.','watersheds',10),
('Climate and biomes','Compare temperature, moisture and biome layers. Explain why some regions are forested while others are dry.','climate',14),
('Build a topographic profile','Measure a cross-section between two points. Record an approximate elevation change and explain vertical exaggeration.','topography',7),
]

def daily_data(user, con):
    """Server-defined UTC challenge. Question IDs are stable for the entire date."""
    today=utcnow().date()
    joined=datetime.fromisoformat(con.execute('SELECT created_at FROM users WHERE id=?',(user['id'],)).fetchone()[0]).date()
    day=max(1,(today-joined).days+1)
    amount=min(20,4+day)  # 5 on day 1, then one extra every day to cap at 20
    # Spread across subjects; slowly introduce the full range of topics.
    topic_count=min(len(set(q[0] for q in QUIZ_BANK)),max(3,2+(day+1)//2))
    topics=sorted(set(q[0] for q in QUIZ_BANK))[:topic_count]
    pool=[i for i,q in enumerate(QUIZ_BANK) if q[0] in topics]
    import random
    rng=random.Random(f"worldforge-v11:{user['id']}:{today.isoformat()}")
    rng.shuffle(pool)
    selected=pool[:min(amount,len(pool))]
    previous=con.execute('SELECT challenge_date,score,total FROM daily_challenges WHERE student_id=? ORDER BY challenge_date DESC LIMIT 35',(user['id'],)).fetchall()
    completed=next((r for r in previous if r['challenge_date']==today.isoformat()),None)
    dates={r['challenge_date'] for r in previous}
    streak=0
    d=today if today.isoformat() in dates else today-timedelta(days=1)
    while d.isoformat() in dates:
        streak+=1;d-=timedelta(days=1)
    return {'day':day,'date':today.isoformat(),'difficulty':min(day,16),'total':len(selected),'topic_count':topic_count,'completed':dict(completed) if completed else None,'streak':streak,'history':[dict(r) for r in previous],'ids':selected}

def utcnow(): return datetime.now(timezone.utc)
def iso(t): return t.isoformat(timespec='seconds')
def db():
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con

def setup():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with LOCK, db() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE NOT NULL,email TEXT UNIQUE NOT NULL,pass_hash TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('student','teacher','parent')),created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,expires_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS assignments(id INTEGER PRIMARY KEY,title TEXT NOT NULL,instructions TEXT NOT NULL,topic TEXT NOT NULL,due_at TEXT NOT NULL,created_by INTEGER REFERENCES users(id),created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS submissions(id INTEGER PRIMARY KEY,assignment_id INTEGER NOT NULL REFERENCES assignments(id),student_id INTEGER NOT NULL REFERENCES users(id),answer TEXT NOT NULL,submitted_at TEXT NOT NULL,grade INTEGER CHECK(grade BETWEEN 0 AND 100),feedback TEXT NOT NULL DEFAULT '',graded_at TEXT,UNIQUE(assignment_id,student_id));
        ''')
        con.executescript("""
        CREATE TABLE IF NOT EXISTS parent_links(parent_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,created_at TEXT NOT NULL,PRIMARY KEY(parent_id,student_id));
        CREATE TABLE IF NOT EXISTS link_codes(code_hash TEXT PRIMARY KEY,student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,expires_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS announcements(id INTEGER PRIMARY KEY,title TEXT NOT NULL,body TEXT NOT NULL,created_by INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS study_goals(id INTEGER PRIMARY KEY,student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0,created_at TEXT NOT NULL);
        """)
        con.execute('''CREATE TABLE IF NOT EXISTS practice_results(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, topic TEXT NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL, completed_at TEXT NOT NULL)''')
        con.execute('''CREATE TABLE IF NOT EXISTS assignment_targets(assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE, student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, PRIMARY KEY(assignment_id,student_id))''')
        con.execute('''CREATE TABLE IF NOT EXISTS daily_challenges(student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, challenge_date TEXT NOT NULL, day_number INTEGER NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL, completed_at TEXT NOT NULL, PRIMARY KEY(student_id,challenge_date))''')
        if con.execute('SELECT count(*) FROM assignments').fetchone()[0] == 0:
            now=utcnow()
            con.executemany('INSERT INTO assignments(title,instructions,topic,due_at,created_at) VALUES(?,?,?,?,?)',[(t,i,p,iso(now+timedelta(days=days)),iso(now)) for t,i,p,days in DEFAULT_ASSIGNMENTS])

def password_hash(password, salt=None):
    salt=salt or secrets.token_bytes(16)
    return salt.hex()+':'+hashlib.pbkdf2_hmac('sha256',password.encode(),salt,260000).hex()
def valid_password(p, saved):
    try:
        s,h=saved.split(':',1)
        return hmac.compare_digest(password_hash(p, bytes.fromhex(s)),saved)
    except (ValueError,TypeError): return False

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory=str(ROOT),**k)
    def send_json(self,status,data,cookie=None):
        body=json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        if cookie: self.send_header('Set-Cookie',cookie)
        self.send_header('Content-Length',str(len(body)))
        self.end_headers();self.wfile.write(body)
    def current(self):
        cookie=SimpleCookie()
        try: cookie.load(self.headers.get('Cookie',''))
        except Exception: return None
        if 'wf_session' not in cookie: return None
        raw=cookie['wf_session'].value
        if len(raw)>150: return None
        token=hashlib.sha256(raw.encode()).hexdigest()
        with db() as con:
            row=con.execute('SELECT users.id,username,email,role,expires_at FROM sessions JOIN users ON users.id=sessions.user_id WHERE token_hash=?',(token,)).fetchone()
        return dict(row) if row and row['expires_at']>iso(utcnow()) else None
    def body(self):
        length=int(self.headers.get('Content-Length','0'))
        if length<1 or length>MAX_BODY: raise ValueError('Invalid request size')
        payload=json.loads(self.rfile.read(length))
        if not isinstance(payload,dict): raise ValueError('Expected JSON object')
        return payload
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/': self.send_response(302);self.send_header('Location','/classroom.html');self.end_headers();return
        if path.startswith('/api/'):
            user=self.current()
            if path=='/api/me': return self.send_json(200,{'user':{k:user[k] for k in ('id','username','email','role')} if user else None})
            if not user: return self.send_json(401,{'error':'Sign in required'})
            if path=='/api/children':
                if user['role']!='parent': return self.send_json(403,{'error':'Parent account required'})
                with db() as con:
                    children=con.execute("""SELECT u.id,u.username FROM parent_links p JOIN users u ON u.id=p.student_id WHERE p.parent_id=? ORDER BY u.username""",(user['id'],)).fetchall()
                    results=[]
                    for child in children:
                        submissions=con.execute('''SELECT a.id AS assignment_id,a.title,a.instructions,a.topic,a.due_at,s.id AS submission_id,s.answer,s.submitted_at,s.grade,s.feedback,a.created_by FROM assignments a LEFT JOIN submissions s ON s.assignment_id=a.id AND s.student_id=? WHERE NOT EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=a.id) OR EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=a.id AND t.student_id=?) ORDER BY a.due_at,a.id''',(child['id'],child['id'])).fetchall()
                        goals=con.execute('SELECT id,title,done FROM study_goals WHERE student_id=? ORDER BY id DESC',(child['id'],)).fetchall()
                        practice=con.execute('SELECT topic,score,total,completed_at FROM practice_results WHERE student_id=? ORDER BY id DESC LIMIT 30',(child['id'],)).fetchall()
                        results.append({'id':child['id'],'username':child['username'],'assignments':[dict(r) for r in submissions],'goals':[dict(r) for r in goals],'practice':[dict(r) for r in practice]})
                return self.send_json(200,{'children':results})
            if path=='/api/announcements':
                with db() as con:
                    rows=con.execute('SELECT a.id,a.title,a.body,a.created_at,u.username AS teacher FROM announcements a JOIN users u ON u.id=a.created_by ORDER BY a.id DESC LIMIT 30').fetchall()
                return self.send_json(200,{'announcements':[dict(r) for r in rows]})
            if path=='/api/daily':
                if user['role']!='student': return self.send_json(403,{'error':'Student account required'})
                with db() as con: d=daily_data(user,con)
                d['questions']=[{'id':i,'question':QUIZ_BANK[i][1],'options':QUIZ_BANK[i][2],'topic':QUIZ_BANK[i][0]} for i in d.pop('ids')]
                return self.send_json(200,d)
            if path=='/api/practice':
                topics=sorted(set(row[0] for row in QUIZ_BANK))
                with db() as con:
                    history=con.execute('SELECT topic,score,total,completed_at FROM practice_results WHERE student_id=? ORDER BY id DESC LIMIT 30',(user['id'],)).fetchall() if user['role']=='student' else []
                return self.send_json(200,{'topics':topics,'questions':[{'id':i,'topic':q[0],'question':q[1],'options':q[2]} for i,q in enumerate(QUIZ_BANK)],'history':[dict(r) for r in history]})
            if path=='/api/goals':
                if user['role']!='student': return self.send_json(403,{'error':'Student account required'})
                with db() as con: rows=con.execute('SELECT id,title,done FROM study_goals WHERE student_id=? ORDER BY id DESC',(user['id'],)).fetchall()
                return self.send_json(200,{'goals':[dict(r) for r in rows]})
            if path=='/api/assignments':
                if user['role']=='parent': return self.send_json(403,{'error':'Use parent dashboard for linked students'})
                with db() as con:
                    if user['role']=='student':
                        rows=con.execute('''SELECT a.*,s.answer,s.submitted_at,s.grade,s.feedback FROM assignments a LEFT JOIN submissions s ON s.assignment_id=a.id AND s.student_id=? WHERE NOT EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=a.id) OR EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=a.id AND t.student_id=?) ORDER BY a.due_at,a.id''',(user['id'],user['id'])).fetchall()
                    else:
                        rows=con.execute('SELECT a.*,(SELECT count(*) FROM submissions s WHERE s.assignment_id=a.id) AS submission_count FROM assignments a WHERE NOT EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=a.id) ORDER BY a.due_at,a.id').fetchall()
                return self.send_json(200,{'assignments':[dict(r) for r in rows]})
            if path=='/api/submissions':
                if user['role']!='teacher': return self.send_json(403,{'error':'Teacher account required'})
                with db() as con:
                    rows=con.execute('''SELECT s.*,u.username AS student,a.title AS assignment_title FROM submissions s JOIN users u ON u.id=s.student_id JOIN assignments a ON a.id=s.assignment_id WHERE NOT EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=s.assignment_id) ORDER BY s.submitted_at DESC''').fetchall()
                return self.send_json(200,{'submissions':[dict(r) for r in rows]})
            return self.send_json(404,{'error':'Unknown endpoint'})
        # Never expose the database, environment files, or backend source over HTTP.
        if path.endswith(('.sqlite3','.sqlite3-wal','.sqlite3-shm','.py','.pyc','.log','.zip')) or any(part.startswith('.') for part in path.split('/') if part):
            return self.send_error(404, 'Not found')
        return super().do_GET()
    def do_POST(self):
        path=urlparse(self.path).path
        if not path.startswith('/api/'): return self.send_json(404,{'error':'Unknown endpoint'})
        # Same-origin JSON requests with custom header prevent ordinary cross-site form POSTs.
        if self.headers.get('X-WorldForge-Request')!='1' or not self.headers.get('Content-Type','').startswith('application/json'):
            return self.send_json(403,{'error':'Invalid request headers'})
        try: data=self.body()
        except (ValueError, json.JSONDecodeError): return self.send_json(400,{'error':'Invalid JSON request'})
        try:
            if path=='/api/signup':
                name=str(data.get('username','')).strip()
                email=str(data.get('email','')).strip().lower()
                password=str(data.get('password',''))
                role=str(data.get('role','student'))
                if not (3<=len(name)<=35 and name.replace('_','').isalnum() and len(email)<=180 and '@' in email and '.' in email.split('@')[-1]): raise ValueError('Enter a valid username and email')
                if not 8<=len(password)<=200: raise ValueError('Password must be at least 8 characters')
                if role not in ('teacher','student','parent'): raise ValueError('Invalid account type')
                if role=='teacher' and (not os.environ.get('WORLDFORGE_TEACHER_CODE') or not hmac.compare_digest(str(data.get('teacher_code','')),os.environ['WORLDFORGE_TEACHER_CODE'])): return self.send_json(403,{'error':'Valid teacher invite code required'})
                with LOCK,db() as con:
                    con.execute('INSERT INTO users(username,email,pass_hash,role,created_at) VALUES(?,?,?,?,?)',(name,email,password_hash(password),role,iso(utcnow())))
                return self.send_json(201,{'ok':True})
            if path=='/api/login':
                name=str(data.get('username','')).strip()
                with db() as con:
                    row=con.execute('SELECT * FROM users WHERE username=? OR email=?',(name,name.lower())).fetchone()
                if not row or not valid_password(str(data.get('password','')),row['pass_hash']): return self.send_json(401,{'error':'Invalid username/email or password'})
                raw=secrets.token_urlsafe(32)
                with LOCK,db() as con:
                    con.execute('INSERT INTO sessions(token_hash,user_id,expires_at) VALUES(?,?,?)',(hashlib.sha256(raw.encode()).hexdigest(),row['id'],iso(utcnow()+timedelta(hours=SESSION_HOURS))))
                return self.send_json(200,{'ok':True},f'wf_session={raw}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_HOURS*3600}')
            if path=='/api/logout':
                cookie=SimpleCookie();cookie.load(self.headers.get('Cookie',''))
                if 'wf_session' in cookie:
                    with LOCK,db() as con: con.execute('DELETE FROM sessions WHERE token_hash=?',(hashlib.sha256(cookie['wf_session'].value.encode()).hexdigest(),))
                return self.send_json(200,{'ok':True},'wf_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
            user=self.current()
            if not user: return self.send_json(401,{'error':'Sign in required'})
            if path=='/api/daily-submit':
                if user['role']!='student': return self.send_json(403,{'error':'Student account required'})
                answers=data.get('answers')
                with LOCK,db() as con:
                    d=daily_data(user,con)
                    if d['completed']: return self.send_json(409,{'error':'Today’s challenge is already completed. Return tomorrow for the next one.'})
                    ids=d['ids']
                    if not isinstance(answers,dict) or set(answers)!=set(map(str,ids)): raise ValueError('Answer every daily question')
                    if any(type(answers[str(i)]) is not int or not 0<=answers[str(i)]<len(QUIZ_BANK[i][2]) for i in ids): raise ValueError('Invalid answer selection')
                    score=sum(answers[str(i)]==QUIZ_BANK[i][3] for i in ids)
                    feedback=[{'id':i,'correct':answers[str(i)]==QUIZ_BANK[i][3],'explanation':QUIZ_BANK[i][4]} for i in ids]
                    con.execute('INSERT INTO daily_challenges(student_id,challenge_date,day_number,score,total,completed_at) VALUES(?,?,?,?,?,?)',(user['id'],d['date'],d['day'],score,len(ids),iso(utcnow())))
                return self.send_json(200,{'score':score,'total':len(ids),'feedback':feedback})
            if path=='/api/practice-submit':
                if user['role']!='student': return self.send_json(403,{'error':'Student account required'})
                topic=str(data.get('topic',''))
                relevant=[(i,q) for i,q in enumerate(QUIZ_BANK) if q[0]==topic]
                answers=data.get('answers')
                if not relevant or not isinstance(answers,dict): raise ValueError('Invalid quiz')
                if set(answers)!=set(str(i) for i,_ in relevant): raise ValueError('Answer every question in this topic')
                for i,q in relevant:
                    a=answers[str(i)]
                    if type(a) is not int or a<0 or a>=len(q[2]): raise ValueError('Choose a valid answer for each question')
                score=sum(answers[str(i)]==q[3] for i,q in relevant)
                feedback=[{'id':i,'correct':answers[str(i)]==q[3],'correct_option':q[3],'explanation':q[4]} for i,q in relevant]
                with LOCK,db() as con:
                    con.execute('INSERT INTO practice_results(student_id,topic,score,total,completed_at) VALUES(?,?,?,?,?)',(user['id'],topic,score,len(relevant),iso(utcnow())))
                return self.send_json(200,{'score':score,'total':len(relevant),'feedback':feedback})
            if path=='/api/link-code':
                if user['role']!='student': return self.send_json(403,{'error':'Student account required'})
                raw=secrets.token_urlsafe(12)
                with LOCK,db() as con:
                    con.execute('DELETE FROM link_codes WHERE student_id=?',(user['id'],))
                    con.execute('INSERT INTO link_codes VALUES(?,?,?)',(hashlib.sha256(raw.encode()).hexdigest(),user['id'],iso(utcnow()+timedelta(minutes=30))))
                return self.send_json(200,{'code':raw,'expires_minutes':30})
            if path=='/api/link-child':
                if user['role']!='parent': return self.send_json(403,{'error':'Parent account required'})
                raw=str(data.get('code','')).strip()
                if not 10<=len(raw)<=100: raise ValueError('Enter a valid student linking code')
                with LOCK,db() as con:
                    row=con.execute('SELECT student_id,expires_at FROM link_codes WHERE code_hash=?',(hashlib.sha256(raw.encode()).hexdigest(),)).fetchone()
                    if not row or row['expires_at']<=iso(utcnow()): return self.send_json(400,{'error':'Code invalid or expired'})
                    con.execute('INSERT OR IGNORE INTO parent_links VALUES(?,?,?)',(user['id'],row['student_id'],iso(utcnow())))
                    con.execute('DELETE FROM link_codes WHERE code_hash=?',(hashlib.sha256(raw.encode()).hexdigest(),))
                return self.send_json(200,{'ok':True})
            if path=='/api/unlink-child':
                if user['role']!='parent': return self.send_json(403,{'error':'Parent account required'})
                child_id=int(data.get('student_id',0))
                with LOCK,db() as con: con.execute('DELETE FROM parent_links WHERE parent_id=? AND student_id=?',(user['id'],child_id))
                return self.send_json(200,{'ok':True})
            if path=='/api/parent-assignment':
                if user['role']!='parent': return self.send_json(403,{'error':'Parent account required'})
                student_id=int(data.get('student_id',0)); title=str(data.get('title','')).strip()
                instructions=str(data.get('instructions','')).strip(); topic=str(data.get('topic','geography')).strip()
                due=str(data.get('due_at','')).strip()
                if not (4<=len(title)<=120 and 12<=len(instructions)<=3000 and 1<=len(topic)<=60): raise ValueError('Check title, topic and instructions')
                try: datetime.strptime(due,'%Y-%m-%d')
                except ValueError: raise ValueError('Due date must be YYYY-MM-DD')
                with LOCK,db() as con:
                    if not con.execute('SELECT 1 FROM parent_links WHERE parent_id=? AND student_id=?',(user['id'],student_id)).fetchone(): return self.send_json(403,{'error':'Student is not linked to this parent'})
                    cursor=con.execute('INSERT INTO assignments(title,instructions,topic,due_at,created_by,created_at) VALUES(?,?,?,?,?,?)',(title,instructions,topic,due+'T23:59:59+00:00',user['id'],iso(utcnow())))
                    con.execute('INSERT INTO assignment_targets(assignment_id,student_id) VALUES(?,?)',(cursor.lastrowid,student_id))
                return self.send_json(201,{'ok':True})
            if path=='/api/parent-grade':
                if user['role']!='parent': return self.send_json(403,{'error':'Parent account required'})
                sid=int(data.get('submission_id',0));grade=int(data.get('grade',-1));feedback=str(data.get('feedback','')).strip()
                if not (0<=grade<=100 and len(feedback)<=2000): raise ValueError('Invalid grade or feedback')
                with LOCK,db() as con:
                    changed=con.execute('''UPDATE submissions SET grade=?,feedback=?,graded_at=? WHERE id=? AND assignment_id IN (SELECT id FROM assignments WHERE created_by=?) AND student_id IN (SELECT student_id FROM parent_links WHERE parent_id=?)''',(grade,feedback,iso(utcnow()),sid,user['id'],user['id']))
                    if not changed.rowcount: return self.send_json(403,{'error':'Not permitted to grade this work'})
                return self.send_json(200,{'ok':True})
            if path=='/api/announcement':
                if user['role']!='teacher': return self.send_json(403,{'error':'Teacher account required'})
                title=str(data.get('title','')).strip(); body=str(data.get('body','')).strip()
                if not 4<=len(title)<=120 or not 10<=len(body)<=2000: raise ValueError('Announcement title or body length invalid')
                with LOCK,db() as con: con.execute('INSERT INTO announcements(title,body,created_by,created_at) VALUES(?,?,?,?)',(title,body,user['id'],iso(utcnow())))
                return self.send_json(201,{'ok':True})
            if path=='/api/goal':
                if user['role']!='student': return self.send_json(403,{'error':'Student account required'})
                title=str(data.get('title','')).strip()
                if not 4<=len(title)<=140: raise ValueError('Goal must be 4–140 characters')
                with LOCK,db() as con: con.execute('INSERT INTO study_goals(student_id,title,created_at) VALUES(?,?,?)',(user['id'],title,iso(utcnow())))
                return self.send_json(201,{'ok':True})
            if path=='/api/toggle-goal':
                if user['role']!='student': return self.send_json(403,{'error':'Student account required'})
                gid=int(data.get('goal_id',0))
                with LOCK,db() as con:
                    changed=con.execute('UPDATE study_goals SET done=1-done WHERE id=? AND student_id=?',(gid,user['id']))
                    if not changed.rowcount:return self.send_json(404,{'error':'Goal not found'})
                return self.send_json(200,{'ok':True})
            if path=='/api/submit':
                if user['role']!='student': return self.send_json(403,{'error':'Student account required'})
                aid=int(data.get('assignment_id',0));answer=str(data.get('answer','')).strip()
                if not 10<=len(answer)<=6000: raise ValueError('Homework answer must be 10–6000 characters')
                with LOCK,db() as con:
                    if not con.execute('''SELECT 1 FROM assignments a WHERE a.id=? AND (NOT EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=a.id) OR EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=a.id AND t.student_id=?))''',(aid,user['id'])).fetchone(): return self.send_json(404,{'error':'Assignment not found'})
                    con.execute('''INSERT INTO submissions(assignment_id,student_id,answer,submitted_at) VALUES(?,?,?,?) ON CONFLICT(assignment_id,student_id) DO UPDATE SET answer=excluded.answer,submitted_at=excluded.submitted_at,grade=NULL,feedback='',graded_at=NULL''',(aid,user['id'],answer,iso(utcnow())))
                return self.send_json(200,{'ok':True})
            if path=='/api/assignment':
                if user['role']!='teacher': return self.send_json(403,{'error':'Teacher account required'})
                title=str(data.get('title','')).strip();instructions=str(data.get('instructions','')).strip();topic=str(data.get('topic','physical')).strip()
                due=str(data.get('due_at','')).strip()
                if not (4<=len(title)<=120 and 12<=len(instructions)<=3000 and 1<=len(topic)<=60): raise ValueError('Title or instructions too short/long')
                try: datetime.strptime(due,'%Y-%m-%d')
                except ValueError: raise ValueError('Due date must be YYYY-MM-DD')
                with LOCK,db() as con:
                    con.execute('INSERT INTO assignments(title,instructions,topic,due_at,created_by,created_at) VALUES(?,?,?,?,?,?)',(title,instructions,topic,due+'T23:59:59+00:00',user['id'],iso(utcnow())))
                return self.send_json(201,{'ok':True})
            if path=='/api/grade':
                if user['role']!='teacher': return self.send_json(403,{'error':'Teacher account required'})
                sid=int(data.get('submission_id',0)); grade=int(data.get('grade',-1)); feedback=str(data.get('feedback','')).strip()
                if not (0<=grade<=100 and len(feedback)<=2000): raise ValueError('Grade must be 0–100 and feedback up to 2000 characters')
                with LOCK,db() as con:
                    change=con.execute('''UPDATE submissions SET grade=?,feedback=?,graded_at=? WHERE id=? AND assignment_id IN (SELECT a.id FROM assignments a WHERE NOT EXISTS (SELECT 1 FROM assignment_targets t WHERE t.assignment_id=a.id))''',(grade,feedback,iso(utcnow()),sid))
                    if not change.rowcount: return self.send_json(404,{'error':'Submission not found'})
                return self.send_json(200,{'ok':True})
            return self.send_json(404,{'error':'Unknown endpoint'})
        except (ValueError, TypeError) as exc: return self.send_json(400,{'error':str(exc)})
        except sqlite3.IntegrityError: return self.send_json(409,{'error':'Username or email already exists'})
    def log_message(self,format,*args): print('%s - %s'%(self.address_string(), format%args))

if __name__=='__main__':
    setup()
    host=os.environ.get('WORLDFORGE_HOST','0.0.0.0')
    port=int(os.environ.get('WORLDFORGE_PORT',os.environ.get('PORT','8081')))
    print(f'WorldForge classroom: http://{host}:{port}/')
    print('Set WORLDFORGE_TEACHER_CODE to enable teacher registration.')
    ThreadingHTTPServer((host,port),Handler).serve_forever()
