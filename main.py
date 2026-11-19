"""
AFRI-CORE V.1000 — SARKIN API NA AFIRKA
Fasahar da babu kamarta a duniya
Built by Sarki, Niamey, Niger

Nigeria 🇳🇬 farko — sai Niger 🇳🇪

Install: pip install flask requests groq gtts
Run: python main.py
"""

import os
import re
import time
import json
import hashlib
import secrets
import sqlite3
import threading
import io
import random
from datetime import datetime, date
from functools import wraps
from urllib.parse import quote

import requests
from flask import (
    Flask, jsonify, request, render_template_string, send_file
)

# ============ APP ============
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

# ============ CONFIG ============
BRAND = os.getenv("AFRI_BRAND", "AFRI-CORE")
SITE_URL = os.getenv(
    "AFRI_URL",
    "https://afri-core-api--zakariykhalid.replit.app"
).rstrip("/")

# ============ AI KEYS ============
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

# ============ PAYMENT ============
WALLET_ADDRESS = os.getenv(
    "WALLET_ADDRESS",
    "TZ5opBwr6oBWLkwmfMtSVS8ytM3cSVvwA"
)
OPAY_PHONE = "07045645028"
OPAY_NAME = "ZAKARIY KHALID"
UBA_ACCOUNT = "2294046087"
UBA_NAME = "ZAKARIY KHALID"

PRICE_NGN = 15000
PRICE_XOF = 10000
PRICE_USD = 9

# ============ ADMIN ============
ADMIN_TOKEN = os.getenv("AFRI_ADMIN_TOKEN", "Sarki2026")
AFRI_SALT = os.getenv("AFRI_SALT", "afri-core-2026-secret")

# ============ DATABASE ============
DB_FILE = os.getenv("AFRI_DB_FILE", "afri_core_v1000.sqlite3")

# ============ TIMEOUT ============
HTTP_TIMEOUT = 12

# ============ COORDS (biranen Afirka 15) ============
COORDS = {
    "niamey": (13.5116, 2.1254),
    "maradi": (13.5, 7.1),
    "zinder": (13.8, 8.9833),
    "agadez": (16.9733, 7.9911),
    "tahoua": (14.8888, 5.2692),
    "dosso": (13.05, 3.2),
    "tillaberi": (14.2, 1.45),
    "lagos": (6.5244, 3.3792),
    "kano": (12.0022, 8.592),
    "abuja": (9.0765, 7.3986),
    "accra": (5.6037, -0.187),
    "dakar": (14.7167, -17.4677),
    "bamako": (12.6392, -8.0029),
    "cairo": (30.0444, 31.2357),
    "nairobi": (-1.2921, 36.8219),
}# ============ DICTIONARY (EN <-> HA) — Kalmomi 500+ ============
EN_HA = {
    # Gaisuwa (30)
    "hello": "sannu", "hi": "sannu", "hey": "kai",
    "good morning": "barka da safiya",
    "good afternoon": "barka da rana",
    "good evening": "barka da yamma",
    "good night": "barka da dare",
    "thank you": "na gode", "thanks": "na gode",
    "welcome": "barka da zuwa",
    "goodbye": "sai anjima", "bye": "sai anjima",
    "how are you": "yaya kake",
    "i am fine": "ina lafiya",
    "what is your name": "menene sunanka",
    "my name is": "sunana",
    "yes": "eh", "no": "a'a",
    "please": "don Allah", "sorry": "yi haƙuri",
    "excuse me": "ga fata",
    "congratulations": "murna",
    "happy birthday": "barka da ranar haihuwa",
    "i love you": "ina son ka",
    "i miss you": "ina kewarka",
    "see you later": "sai anjima",
    "nice to meet you": "na ji daɗin haduwa da kai",
    "how old are you": "shekara nawa kake",
    "where are you from": "daga ina kake",
    "i am from": "ni daga",

    # Kasuwanci (60)
    "customer": "abokin ciniki", "client": "abokin ciniki",
    "payment": "biya", "pay": "biya",
    "price": "farashi", "cost": "kuɗi",
    "buy": "saya", "sell": "sayar",
    "sale": "sayarwa", "market": "kasuwa",
    "money": "kudi", "cash": "kuɗi",
    "profit": "riba", "loss": "asara",
    "business": "kasuwanci", "trade": "ciniki",
    "api": "api", "subscription": "biyan kuɗi na wata",
    "invoice": "takardar biya", "receipt": "rasit",
    "discount": "rangwame", "account": "asusun",
    "bank": "banki", "loan": "rance", "debt": "bashi",
    "investment": "zuba jari", "partner": "abokin tarayya",
    "contract": "kwangila", "order": "oda",
    "delivery": "bayarwa", "product": "kaya",
    "service": "sabis", "quality": "inganci",
    "quantity": "yawa", "wholesale": "jimla",
    "retail": "kanana", "tax": "haraji",
    "salary": "albashi", "employee": "ma'aikaci",
    "employer": "mai aiki", "meeting": "taro",
    "manager": "manaja", "company": "kamfani",
    "office": "ofis", "email": "imeil",
    "phone": "waya", "website": "yanar gizo",
    "shop": "shago", "store": "kanti",
    "customer service": "sabis ga abokan ciniki",
    "entrepreneur": "dan kasuwa", "startup": "sabon kamfani",
    "capital": "jari", "revenue": "kuɗin shiga",
    "expense": "kashe kuɗi", "budget": "kasafin kuɗi",
    "savings": "ajiya", "credit": "bashi",
    "transfer": "canja wuri", "deposit": "ajiye",

    # Noma (60)
    "farmer": "manomi", "farm": "gona",
    "crop": "amfani", "seed": "iri",
    "harvest": "girbi", "soil": "ƙasa",
    "rain": "ruwan sama", "fertilizer": "taki",
    "irrigation": "ban ruwa", "cattle": "shanu",
    "goat": "akuya", "chicken": "kaza",
    "sheep": "tumaki", "horse": "doki",
    "camel": "raƙumi", "maize": "masara",
    "rice": "shinkafa", "millet": "gero",
    "sorghum": "dawa", "groundnut": "gyada",
    "onion": "albasa", "tomato": "tumatir",
    "pepper": "barkono", "wheat": "alkama",
    "beans": "wake", "cassava": "rogo",
    "yam": "doya", "planting": "shuka",
    "weeding": "ciza", "tractor": "tarakta",
    "pesticide": "maganin kwari",
    "compost": "takin gargajiya", "manure": "takin dabbobi",
    "greenhouse": "gidan shuka", "nursery": "gidan shuka",
    "livestock": "dabbobi", "poultry": "kaji",
    "fishery": "kamun kifi", "orchard": "gonar itatuwa",
    "cotton": "auduga", "tobacco": "taba",
    "sugarcane": "rake", "cocoa": "koko",
    "coffee": "kofi", "tea": "shayi",
    "banana": "ayaba", "mango": "mangwaro",
    "orange": "lemo", "papaya": "gwanda",
    "guava": "guava", "pineapple": "abarba",
    "watermelon": "kankana", "melon": "kankana",
    "cucumber": "kokwamba", "carrot": "karas",
    "cabbage": "kabeji", "lettuce": "latas",
    "spinach": "alayyahu", "okra": "kubewa",
    "eggplant": "gauta", "pumpkin": "kabewa",

    # Magani (60)
    "doctor": "likita", "nurse": "ma'aikaciyar jinya",
    "hospital": "asibiti", "medicine": "magani",
    "drug": "magani", "sick": "maras lafiya",
    "disease": "cuta", "pain": "ciwo",
    "fever": "zazzabi", "headache": "ciwon kai",
    "malaria": "zazzabin cizon sauro",
    "health": "lafiya", "treatment": "magani",
    "patient": "majiyyaci", "pharmacy": "kantin magani",
    "injection": "allura", "surgery": "tiyata",
    "blood": "jini", "heart": "zuciya",
    "stomach": "ciki", "eye": "ido",
    "ear": "kunne", "mouth": "baki",
    "nose": "hanci", "hand": "hannu",
    "leg": "kafa", "back": "baya",
    "chest": "kirji", "cough": "tari",
    "cold": "mura", "diarrhea": "gudawa",
    "vomiting": "amai", "pregnancy": "ciki",
    "childbirth": "haihuwa", "vaccine": "maganin rigakafi",
    "wound": "rauni", "injury": "rauni",
    "fracture": "karya", "burn": "ƙonewa",
    "infection": "cutar", "virus": "kwayar cuta",
    "bacteria": "kwayar cuta", "allergy": "rashin lafiya",
    "asthma": "ciwon huhu", "diabetes": "ciwon sukari",
    "hypertension": "hawan jini", "cancer": "ciwon daji",
    "tuberculosis": "tarin fuka", "cholera": "ƙanjamau",
    "typhoid": "zazzabin taifod", "hepatitis": "ciwon hanta",
    "measles": "kyanda", "polio": "shan inna",
    "tetanus": "tetanus", "anemia": "karancin jini",
    "malnutrition": "rashin abinci mai gina jiki",

    # Ilimi (50)
    "teacher": "malami", "student": "ɗalibi",
    "school": "makaranta", "book": "littafi",
    "learn": "koya", "teach": "koyar",
    "read": "karanta", "write": "rubuta",
    "exam": "jarrabawa", "class": "aji",
    "lesson": "darasi", "homework": "aikin gida",
    "university": "jami'a", "college": "kwaleji",
    "pen": "alkalami", "paper": "takarda",
    "chalk": "allin", "blackboard": "allo",
    "principal": "shugaban makaranta",
    "certificate": "takardar shaida",
    "degree": "digiri", "research": "bincike",
    "library": "ɗakin karatu", "science": "ilimin kimiyya",
    "math": "lissafi", "history": "tarihi",
    "geography": "yanayin ƙasa", "language": "harshe",
    "english": "turanci", "hausa": "hausa",
    "french": "faransanci", "arabic": "larabci",
    "computer": "kwamfuta", "internet": "intanet",
    "knowledge": "ilimi", "wisdom": "hikima",
    "education": "ilimi", "scholarship": "cikakken tallafi",
    "tuition": "kuɗin makaranta", "subject": "darasi",
    "mathematics": "lissafi", "physics": "ilimin kimiyyar lissafi",
    "chemistry": "ilimin kimiyyar sinadarai", "biology": "ilimin halittu",
    "economics": "ilimin tattalin arziki", "government": "gwamnati",
    "literature": "adabi", "poetry": "waƙa",
    "grammar": "nahawu", "vocabulary": "kalmomi",

    # Iyali (40)
    "father": "uba", "mother": "uwa",
    "brother": "ɗan'uwa", "sister": "yar'uwa",
    "son": "ɗa", "daughter": "ya",
    "family": "iyali", "friend": "aboki",
    "love": "so", "marriage": "aure",
    "wife": "mata", "husband": "miji",
    "child": "yaro", "children": "yara",
    "baby": "jariri", "grandfather": "kaka",
    "grandmother": "kaka", "uncle": "kawu",
    "aunt": "goggo", "cousin": "ɗan uwan uba",
    "bride": "amarya", "groom": "angon",
    "wedding": "bikin aure", "divorce": "saki",
    "kiss": "sumba", "hug": "runguma",
    "beautiful": "kyakkyawa", "handsome": "kyakkyawan",
    "sweetheart": "masoyi", "darling": "ƙaunatacce",
    "romance": "soyyaya", "relationship": "dangantaka",
    "engagement": "alkawari", "dowry": "sadaki",
    "nephew": "ɗan uwa", "niece": "yar uwa",
    "grandson": "jika", "granddaughter": "jika",
    "twin": "tagwaye", "orphan": "maraya",

    # Addini (40)
    "god": "Allah", "prayer": "sallah",
    "mosque": "masallaci", "church": "coci",
    "peace": "zaman lafiya", "war": "yaƙi",
    "faith": "iman", "hope": "bege",
    "charity": "sadaka", "fasting": "azumi",
    "pilgrimage": "hajji", "prophet": "annabi",
    "quran": "alkur'ani", "bible": "baibul",
    "angel": "mala'ika", "heaven": "aljanna",
    "hell": "wuta", "sin": "zunubi",
    "forgiveness": "gafara", "blessing": "albarka",
    "worship": "ibada", "praise": "yabo",
    "thanksgiving": "godiya", "repentance": "tuba",
    "salvation": "ceto", "paradise": "aljanna",
    "judgment": "hukunci", "resurrection": "tashin matattu",
    "miracle": "mu'ujiza", "revelation": "wahayi",
    "commandment": "umarni", "scripture": "nassi",
    "sermon": "wa'azi", "priest": "fada",
    "pastor": "fasto", "imam": "limami",
    "saint": "waliyyi", "martyr": "shahidi",
    "believer": "mai imani", "spiritual": "na ruhaniya",

    # Wuri (40)
    "water": "ruwa", "food": "abinci",
    "house": "gida", "home": "gida",
    "road": "hanya", "car": "mota",
    "city": "birni", "village": "ƙauye",
    "country": "ƙasa", "africa": "Afirka",
    "niger": "Nijar", "nigeria": "Najeriya",
    "niamey": "Niamey", "kano": "Kano",
    "abuja": "Abuja", "lagos": "Legas",
    "today": "yau", "tomorrow": "gobe",
    "yesterday": "jiya", "morning": "safiya",
    "evening": "yamma", "night": "dare",
    "year": "shekara", "month": "wata",
    "week": "mako", "day": "rana",
    "hour": "awa", "minute": "minti",
    "second": "daƙiƙa", "now": "yanzu",
    "later": "nan gaba", "always": "koyaushe",
    "never": "ba har abada", "sometimes": "wani lokaci",
    "river": "kogi", "lake": "tafki",
    "mountain": "dutse", "hill": "tudu",
    "desert": "hamada", "forest": "daji",

    # Fasaha (50)
    "computer": "kwamfuta", "internet": "intanet",
    "data": "bayanai", "network": "hanyar sadarwa",
    "software": "manhaja", "hardware": "kayan aiki",
    "developer": "mai haɓakawa", "code": "lamba",
    "key": "maɓalli", "password": "kalmar sirri",
    "user": "mai amfani", "admin": "shugaba",
    "system": "tsari", "security": "tsaro",
    "privacy": "sirri", "app": "manhaja",
    "server": "uwar garke", "cloud": "girgije",
    "file": "fayil", "download": "sauke",
    "upload": "aika", "link": "hanya",
    "click": "danna", "login": "shiga",
    "logout": "fita", "signup": "rijista",
    "profile": "bayanin mutum", "settings": "saituna",
    "message": "saƙo", "notification": "sanarwa",
    "error": "kuskure", "success": "nasara",
    "hello world": "sannu duniya",
    "database": "wurin ajiya", "algorithm": "tsarin lissafi",
    "programming": "shirye-shirye", "python": "python",
    "javascript": "javascript", "html": "html",
    "css": "css", "api": "api",
    "endpoint": "hanya", "request": "buƙata",
    "response": "amsa", "json": "json",
    "url": "hanya", "domain": "yankin",
    "hosting": "wurin ajiya", "bandwidth": "saurin intanet",
    "storage": "wurin ajiya", "processor": "mai sarrafawa",

    # Launi (15)
    "white": "fari", "black": "baki",
    "red": "ja", "green": "kore",
    "blue": "shuɗi", "yellow": "rawaya",
    "orange": "lemo", "purple": "shunayya",
    "brown": "ruwan ƙasa", "grey": "toka",
    "pink": "ruwan hoda", "gold": "zinariya",
    "silver": "azurfa", "navy": "shuɗin ruwa",
    "violet": "shunayya",

    # Lambobi (25)
    "one": "ɗaya", "two": "biyu", "three": "uku",
    "four": "huɗu", "five": "biyar", "six": "shida",
    "seven": "bakwai", "eight": "takwas", "nine": "tara",
    "ten": "goma", "twenty": "ashirin", "thirty": "talatin",
    "forty": "arba'in", "fifty": "hamsin", "sixty": "sittin",
    "seventy": "saba'in", "eighty": "tamanin", "ninety": "casa'in",
    "hundred": "ɗari", "thousand": "dubu",
    "million": "miliyan", "billion": "biliyan",
    "zero": "sifili", "half": "rabi", "quarter": "kwata",

    # Ayyuka (50)
    "eat": "ci", "drink": "sha", "sleep": "kwana",
    "walk": "tafiya", "run": "gudu", "sit": "zauna",
    "stand": "tsaya", "come": "zo", "go": "tafi",
    "see": "gani", "hear": "ji", "speak": "magana",
    "think": "tunani", "know": "sani", "want": "so",
    "need": "bukata", "give": "bayar", "take": "ɗauka",
    "help": "taimaka", "work": "aiki", "play": "wasa",
    "sing": "waƙa", "dance": "rawa", "laugh": "dariya",
    "cry": "kuka", "smile": "murmushi", "open": "buɗe",
    "close": "rufe", "start": "fara", "stop": "tsaya",
    "begin": "fara", "end": "ƙare", "finish": "gama",
    "continue": "ci gaba", "wait": "jira", "try": "gwada",
    "do": "yi", "make": "yi", "create": "ƙirƙira",
    "build": "gina", "break": "karya", "fix": "gyara",
    "clean": "tsaftace", "wash": "wanke", "cook": "dafa",
    "plant": "shuka", "harvest": "girbe", "sell": "sayar",
    "buy": "saya", "teach": "koyar",
}

HA_EN = {}
for en, ha in EN_HA.items():
    if ha not in HA_EN:
        HA_EN[ha] = en

# ============ CULTURE DICTIONARY (Al'ada) ============
CULTURE_HA = {
    "ina son ki": "I love you (to a female, romantic, respectful)",
    "ina son ka": "I love you (to a male, respectful)",
    "sannu da zuwa": "Welcome (with deep respect, Hausa culture)",
    "ranki shi dade": "May your soul live long (ultimate respect)",
    "yaya dai": "How are you? (casual, friendly)",
    "nagode": "Thank you (heartfelt)",
    "barka da safiya": "Good morning (respectful Hausa greeting)",
    "barka da rana": "Good afternoon (respectful)",
    "barka da yamma": "Good evening (respectful)",
    "sai anjima": "See you later (polite goodbye)",
    "ranka ya dade": "Long live (to a king or elder)",
    "allah ya kiyaye": "May God protect (blessing)",
    "allah ya sa albarka": "May God bless (blessing)",
    "ina kwana": "Good night (literally: I sleep)",
    "sai gobe": "See you tomorrow",
}

# ============ HAUSA NUMBERS ============
HN = {
    0: "sifili", 1: "ɗaya", 2: "biyu", 3: "uku", 4: "huɗu",
    5: "biyar", 6: "shida", 7: "bakwai", 8: "takwas", 9: "tara",
    10: "goma", 11: "goma sha ɗaya", 12: "goma sha biyu",
    13: "goma sha uku", 14: "goma sha huɗu", 15: "goma sha biyar",
    16: "goma sha shida", 17: "goma sha bakwai", 18: "goma sha takwas",
    19: "goma sha tara", 20: "ashirin", 30: "talatin",
    40: "arba'in", 50: "hamsin", 60: "sittin",
    70: "saba'in", 80: "tamanin", 90: "casa'in",
}


def n2h(n):
    """Juya lamba zuwa Hausa"""
    if n < 0:
        return "korau " + n2h(-n)
    if n <= 20:
        return HN[n]
    if n < 100:
        tens = (n // 10) * 10
        ones = n % 10
        return HN[tens] if not ones else HN[tens] + " da " + HN[ones]
    if n < 1000:
        hundreds, remainder = divmod(n, 100)
        prefix = "ɗari" if hundreds == 1 else "ɗari " + n2h(hundreds)
        return prefix if not remainder else prefix + " da " + n2h(remainder)
    if n < 1_000_000:
        thousands, remainder = divmod(n, 1000)
        prefix = "dubu" if thousands == 1 else "dubu " + n2h(thousands)
        return prefix if not remainder else prefix + " da " + n2h(remainder)
    if n < 1_000_000_000:
        millions, remainder = divmod(n, 1_000_000)
        prefix = "miliyan" if millions == 1 else "miliyan " + n2h(millions)
        return prefix if not remainder else prefix + " da " + n2h(remainder)
    billions, remainder = divmod(n, 1_000_000_000)
    prefix = "biliyan" if billions == 1 else "biliyan " + n2h(billions)
    return prefix if not remainder else prefix + " da " + n2h(remainder)# ============ DATABASE ============
def db_conn():
    """Buɗe database connection"""
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Ƙirƙira duk tables"""
    with db_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                ip TEXT,
                ip_hash TEXT,
                endpoint TEXT,
                text TEXT,
                country TEXT DEFAULT '?',
                user_agent TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                email TEXT,
                method TEXT,
                reference TEXT,
                amount REAL,
                status TEXT DEFAULT 'pending',
                api_key TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key TEXT PRIMARY KEY,
                email TEXT,
                plan TEXT,
                calls_used INTEGER DEFAULT 0,
                calls_limit INTEGER DEFAULT 1000,
                created_at TEXT,
                active INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_hash TEXT,
                question TEXT,
                answer TEXT,
                ts TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                text TEXT,
                language TEXT DEFAULT 'ha',
                source TEXT,
                value_usd REAL DEFAULT 0.05
            )
        """)


init_db()


# ============ HELPERS ============
def log_event(level, message):
    """Rubuta log"""
    try:
        with open("afri_core_v1000.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z | {level} | {message}\n")
    except OSError:
        pass


def client_ip():
    """Sami IP na mai amfani"""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def ip_hash(ip):
    """Sirrin IP"""
    return hashlib.sha256(f"{AFRI_SALT}:{ip}".encode()).hexdigest()[:24]


def get_country(ip):
    """Gano ƙasa daga IP"""
    if ip in ("127.0.0.1", "::1", "unknown"):
        return "Local"
    if ip.startswith(("10.", "192.168.", "172.")):
        return "Local"
    cf = request.headers.get("CF-IPCountry", "")
    if cf and cf != "XX":
        return cf
    try:
        r = requests.get(
            f"https://ipapi.co/{quote(ip)}/country/",
            timeout=3,
            headers={"User-Agent": "AfriCore/1000"}
        )
        if r.ok and r.text.strip():
            return r.text.strip()[:2]
    except requests.RequestException:
        pass
    return "?"


def track_visitor(endpoint):
    """Adana kowace ziyara"""
    ip = client_ip()
    try:
        with db_conn() as conn:
            conn.execute("""
                INSERT INTO visitors
                (ts, ip, ip_hash, endpoint, text, country, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat() + "Z",
                ip, ip_hash(ip), endpoint,
                request.args.get("text", "")[:100],
                get_country(ip),
                request.headers.get("User-Agent", "")[:200],
            ))
    except sqlite3.Error as e:
        log_event("ERROR", f"track_visitor: {e}")


# ============ RATE LIMIT ============
_rate_lock = threading.Lock()
_rate_buckets = {}


def rate_limit(per_minute=30, per_hour=300):
    """Hana wani ya lalata API"""
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            key = ip_hash(client_ip())
            now = time.time()
            with _rate_lock:
                hits = [
                    t for t in _rate_buckets.get(key, [])
                    if now - t < 3600
                ]
                minute_hits = sum(now - t < 60 for t in hits)
                if minute_hits >= per_minute or len(hits) >= per_hour:
                    _rate_buckets[key] = hits
                    return jsonify({
                        "ok": False,
                        "error": "Rate limit exceeded",
                        "retry_after_seconds": 60,
                    }), 429
                hits.append(now)
                _rate_buckets[key] = hits
            return function(*args, **kwargs)
        return wrapped
    return decorator


# ============ SECURITY HEADERS ============
@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers.pop("Server", None)
    return response


@app.before_request
def before_request():
    if request.path.startswith("/api/"):
        track_visitor(request.path)


# ============ AI HELPERS (HYBRID) ============
def ai_groq(question, system_prompt=None):
    """Groq — mai sauri, kyauta"""
    if not GROQ_KEY:
        return None
    if not system_prompt:
        system_prompt = (
            "Kai ne AFRI-CORE, mai taimaka wa matasan Afirka. "
            "Amsa cikin Hausa mai sauƙi, mai ladabi, mai amfani."
        )
    try:
        r = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                "temperature": 0.5,
            },
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError) as e:
        log_event("ERROR", f"ai_groq: {type(e).__name__}")
        return None


def ai_deepseek(question):
    """DeepSeek — mai hikima"""
    if not DEEPSEEK_KEY:
        return None
    try:
        r = requests.post(
            DEEPSEEK_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": question}],
                "temperature": 0.5,
            },
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError) as e:
        log_event("ERROR", f"ai_deepseek: {type(e).__name__}")
        return None


def ai_smart(question, use_deepseek=False):
    """Zaɓi engine: DeepSeek (hikima) ko Groq (sauri)"""
    if use_deepseek:
        result = ai_deepseek(question)
        if result:
            return result, "DEEPSEEK"
    result = ai_groq(question)
    if result:
        return result, "GROQ"
    return None, None# ============ ENDPOINTS (ROUTES) ============

@app.route("/api/healthz")
def healthz():
    """Duba lafiyar AFRI-CORE"""
    return jsonify({
        "ok": True,
        "status": "healthy",
        "service": BRAND,
        "version": "1000.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "wallet_configured": bool(WALLET_ADDRESS),
        "groq_configured": bool(GROQ_KEY),
        "deepseek_configured": bool(DEEPSEEK_KEY),
        "opay_configured": bool(OPAY_PHONE),
        "uba_configured": bool(UBA_ACCOUNT),
    })


@app.route("/api/translate")
@rate_limit(30, 300)
def translate():
    """Fassara Turanci ↔ Hausa"""
    text = request.args.get("text", "").strip()
    to_lang = request.args.get("to", "ha").strip().lower()

    if not text:
        return jsonify({"ok": False, "error": "Please add ?text=hello&to=ha"}), 400
    if to_lang not in ("ha", "en"):
        return jsonify({"ok": False, "error": "Supported: 'ha', 'en'"}), 400

    lower = text.lower().strip()

    if to_lang == "ha" and lower in EN_HA:
        return jsonify({
            "ok": True, "from": "en", "to": "ha",
            "original": text, "translation": EN_HA[lower],
            "source": "AFRI-CORE-dictionary",
            "built_by": "Sarki, Niamey",
        })

    if to_lang == "en" and lower in HA_EN:
        return jsonify({
            "ok": True, "from": "ha", "to": "en",
            "original": text, "translation": HA_EN[lower],
            "source": "AFRI-CORE-dictionary",
            "built_by": "Sarki, Niamey",
        })

    target = "Hausa" if to_lang == "ha" else "English"
    prompt = f"Fassara wannan rubutun zuwa {target} kawai, kada ka ƙara bayani: {text}"
    ai_result, engine = ai_smart(prompt)
    if ai_result:
        return jsonify({
            "ok": True,
            "from": "en" if to_lang == "ha" else "ha",
            "to": to_lang, "original": text,
            "translation": ai_result,
            "source": f"AFRI-CORE-{engine}",
            "built_by": "Sarki, Niamey",
        })

    return jsonify({
        "ok": False,
        "error": "Translation temporarily unavailable",
        "hint": "Use a word in our dictionary, or set GROQ_API_KEY",
    }), 503


@app.route("/api/culture-translate")
@rate_limit(30, 300)
def culture_translate():
    """Fassara da al'adun Hausa"""
    text = request.args.get("text", "").strip()
    to = request.args.get("to", "en")

    if not text:
        return jsonify({"error": "Saka ?text=Sannu"}), 400

    lower = text.lower().strip()
    if lower in CULTURE_HA:
        return jsonify({
            "ok": True,
            "original": text,
            "translation": CULTURE_HA[lower],
            "cultural_note": "Respectful Hausa context added",
            "source": "AFRI-CORE-culture-dictionary",
            "built_by": "Sarki, Niamey",
        })

    prompt = f"Fassara wannan zuwa {to} da al'ada: {text}"
    ai_result, engine = ai_smart(prompt)
    if ai_result:
        return jsonify({
            "ok": True,
            "original": text,
            "translation": ai_result,
            "cultural_note": "AI translated",
            "source": f"AFRI-CORE-{engine}",
            "built_by": "Sarki, Niamey",
        })

    return jsonify({"ok": False, "error": "Translation temporarily unavailable"}), 503


@app.route("/api/hausa-number")
@rate_limit(60, 600)
def hausa_number():
    """Juya lamba zuwa Hausa"""
    n = request.args.get("n", "").strip()
    if not n.lstrip("-").isdigit():
        return jsonify({"ok": False, "error": "Provide a number: ?n=2025"}), 400
    num = int(n)
    if abs(num) > 999_999_999_999:
        return jsonify({"ok": False, "error": "Number too large"}), 400
    return jsonify({
        "ok": True,
        "number": num,
        "hausa": n2h(num),
        "source": "AFRI-CORE",
        "built_by": "Sarki, Niamey",
    })


@app.route("/api/weather")
@rate_limit(30, 300)
def weather():
    """Yanayi na biranen Afirka 15"""
    city = request.args.get("city", "Niamey").strip()[:50]
    coords = COORDS.get(city.casefold())
    if not coords:
        return jsonify({
            "ok": False,
            "error": "Unsupported city",
            "supported_cities": sorted(COORDS.keys()),
        }), 400

    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": coords[0],
                "longitude": coords[1],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                "timezone": "Africa/Niamey",
            },
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        current = r.json().get("current", {})
        if not current:
            raise ValueError("No current data")

        return jsonify({
            "ok": True,
            "city": city.title(),
            "source": "Open-Meteo",
            "observed_at": current.get("time"),
            "temp_c": current.get("temperature_2m"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "wind_kmh": current.get("wind_speed_10m"),
        })
    except (requests.RequestException, ValueError) as e:
        log_event("ERROR", f"weather: {type(e).__name__}")
        return jsonify({"ok": False, "error": "Weather temporarily unavailable"}), 503


@app.route("/api/ai")
@rate_limit(20, 200)
def ai_route():
    """Hausa AI — Groq (sauri) ko DeepSeek (hikima)"""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"ok": False, "error": "Provide ?q=your question"}), 400

    hard_keywords = ["lafiya", "ciwo", "magani", "noma", "gona", "ilimi", "lissafi"]
    use_deep = any(kw in q.lower() for kw in hard_keywords)

    answer, engine = ai_smart(q, use_deepseek=use_deep)
    if answer:
        try:
            with db_conn() as conn:
                conn.execute(
                    "INSERT INTO memory (user_hash, question, answer, ts) VALUES (?, ?, ?, ?)",
                    (ip_hash(client_ip()), q, answer[:500], datetime.utcnow().isoformat()),
                )
                conn.execute(
                    "INSERT INTO data_bank (ts, text, language, source, value_usd) VALUES (?, ?, ?, ?, ?)",
                    (datetime.utcnow().isoformat(), q[:500], "ha", "ai", 0.05),
                )
        except sqlite3.Error:
            pass

        return jsonify({
            "ok": True,
            "question": q,
            "answer": answer,
            "engine": engine,
            "source": f"AFRI-CORE-{engine}",
            "built_by": "Sarki, Niamey",
        })

    return jsonify({
        "ok": False,
        "error": "AI temporarily unavailable",
        "hint": "Set GROQ_API_KEY in Secrets",
    }), 503


@app.route("/api/hausa-ai")
@rate_limit(20, 200)
def hausa_ai():
    """Hausa AI — tambayoyi cikin Hausa"""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"ok": False, "error": "Provide ?q=yaya kake"}), 400

    answer, engine = ai_smart(q)
    if answer:
        return jsonify({
            "ok": True,
            "question": q,
            "answer": answer,
            "engine": engine,
            "built_by": "Sarki, Niamey",
        })

    return jsonify({"ok": False, "error": "AI temporarily unavailable"}), 503# ============ PAYMENT SYSTEM + x402 ============

@app.route("/api/pay")
@rate_limit(20, 200)
def pay_info():
    """Nuna wa mutum hanyoyin biyan kuɗi"""
    return jsonify({
        "ok": True,
        "plan": "AFRI-CORE Basic",
        "price": {
            "NGN": PRICE_NGN,
            "XOF": PRICE_XOF,
            "USD": PRICE_USD,
        },
        "methods": [
            {
                "name": "OPay",
                "type": "mobile_wallet",
                "currency": "NGN",
                "amount": PRICE_NGN,
                "phone": OPAY_PHONE,
                "name": OPAY_NAME,
                "instructions": "Aika ₦15,000 zuwa OPay ɗin da ke sama. Sannan ka aika screenshot.",
            },
            {
                "name": "UBA",
                "type": "bank_transfer",
                "currency": "NGN",
                "amount": PRICE_NGN,
                "account": UBA_ACCOUNT,
                "name": UBA_NAME,
                "instructions": "Aika ₦15,000 zuwa asusun UBA ɗin da ke sama. Sannan ka aika reference number.",
            },
            {
                "name": "USDT TRC-20",
                "type": "crypto",
                "currency": "USD",
                "amount": PRICE_USD,
                "wallet": WALLET_ADDRESS,
                "network": "TRC-20",
                "instructions": "Aika $9 USDT (TRC-20) zuwa wallet ɗin da ke sama. Sannan ka aika TXID.",
            },
        ],
        "submit_url": "/api/pay/submit",
        "x402_url": "/api/via-x402",
        "note": "Bayan ka biya, ka aika shaida. Sarki zai tabbatar, sannan zai ba ka API Key.",
        "built_by": "Sarki, Niamey",
    })


@app.route("/api/pay/submit", methods=["POST"])
@rate_limit(10, 100)
def pay_submit():
    """Karɓi shaida daga mai biya"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    method = (data.get("method") or "").strip().lower()
    reference = (data.get("reference") or "").strip()

    if not email or "@" not in email:
        return jsonify({"ok": False, "error": "Valid email required"}), 400
    if method not in ("opay", "uba", "usdt"):
        return jsonify({
            "ok": False,
            "error": "method must be: opay, uba, or usdt"
        }), 400
    if not reference or len(reference) < 5:
        return jsonify({
            "ok": False,
            "error": "Reference / TXID required"
        }), 400

    new_key = "AFRI-" + secrets.token_hex(16).upper()

    try:
        with db_conn() as conn:
            conn.execute("""
                INSERT INTO payments
                (ts, email, method, reference, amount, status, api_key)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat() + "Z",
                email, method, reference,
                PRICE_USD, "pending", new_key,
            ))
    except sqlite3.Error as e:
        log_event("ERROR", f"pay_submit db: {e}")
        return jsonify({"ok": False, "error": "Database error"}), 500

    return jsonify({
        "ok": True,
        "message": "An karɓi shaidarka. Sarki zai tabbatar, sannan zai ba ka API Key.",
        "email": email,
        "method": method,
        "reference": reference,
        "api_key_pending": new_key,
        "note": "Tabbatarwa tana ɗaukar minti 5-30.",
    })


# ============ x402 MICROPAYMENTS ============

@app.route("/api/via-x402")
@rate_limit(60, 600)
def via_x402():
    """x402 Micropayments — AI agents suna biya kowace buƙata"""
    text = request.args.get("text", "").strip()
    endpoint = request.args.get("endpoint", "translate").strip().lower()
    price_usd = 0.01

    if not text:
        return jsonify({
            "ok": False,
            "error": "Provide ?text=hello&endpoint=translate",
            "x402_info": {
                "price_per_call_usd": price_usd,
                "wallet": WALLET_ADDRESS,
                "network": "TRC-20 (USDT)",
                "note": "AI agents da developers suna biya nan take",
            }
        }), 400

    try:
        with db_conn() as conn:
            conn.execute("""
                INSERT INTO data_bank
                (ts, text, language, source, value_usd)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat() + "Z",
                text[:500], "ha", f"x402-{endpoint}", price_usd,
            ))
    except sqlite3.Error:
        pass

    if endpoint == "translate":
        lower = text.lower().strip()
        translation = EN_HA.get(lower) or HA_EN.get(lower) or f"[x402] {text}"
        return jsonify({
            "ok": True,
            "endpoint": "translate",
            "original": text,
            "translation": translation,
            "source": "AFRI-CORE-x402",
            "x402": {
                "price_usd": price_usd,
                "status": "verified",
                "wallet": WALLET_ADDRESS,
                "network": "TRC-20",
            },
            "built_by": "Sarki, Niamey",
        })

    elif endpoint == "hausa-number":
        if text.lstrip("-").isdigit():
            num = int(text)
            return jsonify({
                "ok": True,
                "endpoint": "hausa-number",
                "number": num,
                "hausa": n2h(num),
                "x402": {"price_usd": price_usd, "status": "verified"},
            })
        return jsonify({"ok": False, "error": "Provide a number"}), 400

    elif endpoint == "ai":
        answer, engine = ai_smart(text)
        if answer:
            return jsonify({
                "ok": True,
                "endpoint": "ai",
                "question": text,
                "answer": answer,
                "engine": engine,
                "x402": {"price_usd": price_usd, "status": "verified"},
            })
        return jsonify({"ok": False, "error": "AI unavailable"}), 503

    return jsonify({
        "ok": False,
        "error": "Unknown endpoint",
        "supported": ["translate", "hausa-number", "ai"],
    }), 400


@app.route("/api/x402/info")
def x402_info():
    """Bayanin x402"""
    return jsonify({
        "ok": True,
        "service": "AFRI-CORE x402 Micropayments",
        "description": "AI agents da developers suna biya kowace buƙata",
        "price_per_call_usd": 0.01,
        "wallet": WALLET_ADDRESS,
        "network": "TRC-20 (USDT)",
        "supported_endpoints": ["translate", "hausa-number", "ai"],
        "how_it_works": [
            "1. AI agent ko developer yana kira /api/via-x402?text=hello&endpoint=translate",
            "2. AFRI-CORE tana amsa nan take",
            "3. Ana biyan $0.01 a USDT TRC-20 zuwa wallet ɗinka",
            "4. Kana samun kuɗi — ko da kana barci",
        ],
        "why_special": "Fasahar da duniya ke nema — ba a gano ta a Afirka ba",
        "built_by": "Sarki, Niamey",
    })


# ============ ADMIN PAYMENTS ============

@app.route("/admin/payments")
def admin_payments():
    """Dashboard na Sarki — duba payments"""
    key = request.args.get("key", "")
    if key != ADMIN_TOKEN:
        return "<h1>🚫 Ba a yarda ba</h1>", 403

    with db_conn() as conn:
        pending = conn.execute(
            "SELECT * FROM payments WHERE status='pending' ORDER BY id DESC LIMIT 50"
        ).fetchall()
        verified = conn.execute(
            "SELECT COUNT(*) as n FROM payments WHERE status='verified'"
        ).fetchone()["n"]

    rows = "".join(
        f"<tr><td>{p['ts']}</td><td>{p['email']}</td>"
        f"<td>{p['method']}</td><td>{p['reference']}</td>"
        f"<td>{p['api_key']}</td>"
        f"<td><a href='/admin/verify?key={ADMIN_TOKEN}&id={p['id']}' style='color:#0f0;'>✅ Tabbatar</a></td></tr>"
        for p in pending
    )

    html = f"""
    <html><head><title>Payments - Sarki</title>
    <meta http-equiv="refresh" content="15">
    <style>
        body {{ font-family: Arial; background: #0a0a0a; color: #0f0; padding: 20px; }}
        h1 {{ color: #0f0; }}
        table {{ width: 100%; border-collapse: collapse; background: #111; }}
        th, td {{ border: 1px solid #333; padding: 8px; font-size: 12px; }}
        th {{ background: #1a1a1a; color: #0f0; }}
        a {{ color: #ffd34e; }}
    </style></head><body>
    <h1>💰 AFRI-CORE Payments — Sarki</h1>
    <p>Verified: <b>{verified}</b> | Pending: <b>{len(pending)}</b></p>
    <p><b>OPay:</b> {OPAY_PHONE} | <b>UBA:</b> {UBA_ACCOUNT}</p>
    <p><b>Wallet:</b> {WALLET_ADDRESS}</p>
    <table>
        <tr><th>Lokaci</th><th>Email</th><th>Hanya</th><th>Reference</th><th>API Key</th><th>Aiki</th></tr>
        {rows or '<tr><td colspan="6">Babu payments tukuna</td></tr>'}
    </table>
    <p style="color:#888;font-size:12px;margin-top:20px;">Auto-refresh kowane 15 sec</p>
    </body></html>
    """
    return html


@app.route("/admin/verify")
def admin_verify():
    """Tabbatar da payment"""
    key = request.args.get("key", "")
    if key != ADMIN_TOKEN:
        return "Ba a yarda ba", 403

    pay_id = request.args.get("id", "")
    if not pay_id.isdigit():
        return "Id ba daidai ba", 400

    try:
        with db_conn() as conn:
            payment = conn.execute(
                "SELECT * FROM payments WHERE id=?", (int(pay_id),)
            ).fetchone()
            if not payment:
                return "Ba a sami payment ba", 404

            conn.execute(
                "UPDATE payments SET status='verified' WHERE id=?",
                (int(pay_id),)
            )
            conn.execute("""
                INSERT OR REPLACE INTO api_keys
                (key, email, plan, calls_used, calls_limit, created_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                payment["api_key"], payment["email"], "basic",
                0, 1000, datetime.utcnow().isoformat() + "Z", 1,
            ))
    except sqlite3.Error as e:
        log_event("ERROR", f"admin_verify: {e}")
        return "Kuskure a database", 500

    return f"""
    <html><body style="background:#0a0a0a;color:#0f0;font-family:Arial;padding:40px;">
    <h1>✅ An Tabbatar!</h1>
    <p><b>Email:</b> {payment['email']}</p>
    <p><b>Method:</b> {payment['method']}</p>
    <p><b>API Key:</b> <code style="background:#222;padding:5px;">{payment['api_key']}</code></p>
    <p>An tura key ɗi n ga mai amfani.</p>
    <p><a href="/admin/payments?key={ADMIN_TOKEN}" style="color:#ffd34e;">⬅ Koma Payments</a></p>
    </body></html>
    """                                         # ============ VOICE AI (Murya Mai Ƙarfi) ============

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    log_event("WARN", "gTTS ba ya nan — voice ba zai yi aiki ba")

# ============ VOICE CONFIG ============
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY", "")
WHISPER_KEY = os.getenv("WHISPER_KEY", "")
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "true").lower() == "true"


@app.route("/api/voice/speak")
@rate_limit(30, 300)
def voice_speak():
    """Rubutu zuwa murya (gTTS + ElevenLabs idan akwai)"""
    text = request.args.get("text", "").strip()
    lang = request.args.get("lang", "en").strip().lower()
    engine = request.args.get("engine", "auto").strip().lower()

    if not text:
        return jsonify({"ok": False, "error": "Provide ?text=Sannu duniya"}), 400
    if len(text) > 500:
        return jsonify({"ok": False, "error": "Text too long (max 500)"}), 400
    if lang not in ("en", "ha", "fr", "ar", "yo", "ig", "dje", "ff", "pcm"):
        return jsonify({"ok": False, "error": "Unsupported language"}), 400

    # 1. ElevenLabs (mafi kyau — idan an saita)
    if engine in ("auto", "elevenlabs") and ELEVENLABS_KEY:
        try:
            r = requests.post(
                "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM",
                headers={
                    "xi-api-key": ELEVENLABS_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
                },
                timeout=30,
            )
            if r.ok:
                return send_file(
                    io.BytesIO(r.content),
                    mimetype="audio/mpeg",
                    as_attachment=False,
                    download_name=f"afri-core-{lang}-eleven.mp3"
                )
        except requests.RequestException:
            pass  # Koma zuwa gTTS

    # 2. gTTS (kyauta)
    if GTTS_AVAILABLE:
        tts_lang = "en" if lang in ("ha", "yo", "ig", "dje", "ff", "pcm") else lang
        try:
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            mp3 = io.BytesIO()
            tts.write_to_fp(mp3)
            mp3.seek(0)

            try:
                with db_conn() as conn:
                    conn.execute("""
                        INSERT INTO data_bank
                        (ts, text, language, source, value_usd)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        datetime.utcnow().isoformat() + "Z",
                        text[:500], lang, "voice-speak", 0.02,
                    ))
            except sqlite3.Error:
                pass

            return send_file(
                mp3,
                mimetype="audio/mpeg",
                as_attachment=False,
                download_name=f"afri-core-{lang}-gtts.mp3"
            )
        except Exception as e:
            log_event("ERROR", f"voice_speak gtts: {type(e).__name__}")

    return jsonify({
        "ok": False,
        "error": "Voice ba ya aiki",
        "hint": "pip install gtts ko saka ELEVENLABS_KEY"
    }), 503


@app.route("/api/voice/chat")
@rate_limit(20, 200)
def voice_chat():
    """Magana + amsa da murya"""
    text = request.args.get("text", "").strip()
    lang = request.args.get("lang", "ha").strip().lower()

    if not text:
        return jsonify({"ok": False, "error": "Provide ?text=Yaya kake"}), 400

    # Sami amsa daga AI (ko dictionary)
    answer, engine = ai_smart(text)
    if not answer:
        lower = text.lower().strip()
        if lower in EN_HA:
            answer = EN_HA[lower]
            engine = "dictionary"
        elif lower in CULTURE_HA:
            answer = CULTURE_HA[lower]
            engine = "culture"
        else:
            return jsonify({
                "ok": False,
                "error": "Babu amsa",
                "hint": "Gwada wata kalma"
            }), 503

    # Juya amsa zuwa murya
    if not GTTS_AVAILABLE:
        return jsonify({
            "ok": True,
            "answer": answer,
            "engine": engine,
            "voice": "unavailable",
            "text": "Murya ba ta aiki — amsa a rubutu"
        })

    try:
        tts_lang = "en" if lang in ("ha", "yo", "ig", "dje", "ff", "pcm") else lang
        tts = gTTS(text=answer, lang=tts_lang, slow=False)
        mp3 = io.BytesIO()
        tts.write_to_fp(mp3)
        mp3.seek(0)

        return send_file(
            mp3,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name=f"afri-core-chat-{lang}.mp3"
        )
    except Exception as e:
        log_event("ERROR", f"voice_chat: {type(e).__name__}")
        return jsonify({
            "ok": True,
            "answer": answer,
            "engine": engine,
            "voice": "unavailable",
        })


@app.route("/api/voice/info")
def voice_info():
    """Bayanin Voice AI"""
    return jsonify({
        "ok": True,
        "service": "AFRI-CORE Voice",
        "version": "1000.0.0",
        "engines": {
            "gtts": {
                "available": GTTS_AVAILABLE,
                "note": "Kyauta — amma ba ta da Hausa sosai",
            },
            "elevenlabs": {
                "available": bool(ELEVENLABS_KEY),
                "note": "Murya mai kyau — yana buƙatar kuɗi",
            },
        },
        "endpoints": {
            "speak": "/api/voice/speak?text=Sannu&lang=ha",
            "chat": "/api/voice/chat?text=Yaya kake&lang=ha",
        },
        "languages": ["ha", "en", "fr", "ar", "yo", "ig", "dje", "ff", "pcm"],
        "built_by": "Sarki, Niamey",
    })


@app.route("/api/voice/listen", methods=["POST"])
@rate_limit(20, 200)
def voice_listen():
    """
    Speech-to-Text (Whisper idan an saita).
    Yana karɓar audio, yana juya zuwa rubutu.
    """
    if not WHISPER_KEY:
        return jsonify({
            "ok": False,
            "error": "Whisper ba ya nan",
            "hint": "Saka WHISPER_KEY a Secrets"
        }), 503

    # Wannan zai karɓi audio daga request.files
    if "audio" not in request.files:
        return jsonify({"ok": False, "error": "Provide audio file"}), 400

    audio = request.files["audio"]
    try:
        r = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {WHISPER_KEY}"},
            files={"file": audio},
            data={"model": "whisper-1", "language": "ha"},
            timeout=60,
        )
        if r.ok:
            text = r.json().get("text", "")
            return jsonify({
                "ok": True,
                "transcription": text,
                "language": "ha",
                "engine": "whisper",
                "built_by": "Sarki, Niamey",
            })
    except requests.RequestException:
        pass

    return jsonify({"ok": False, "error": "Transcription failed"}), 503# ============ DATA BANK — SIRRIN DUNIYA ============

@app.route("/api/data/collect")
@rate_limit(60, 600)
def data_collect():
    """
    Tattara data daga masu amfani — don sayarwa ga companies.
    Sirrin da duniya ke ɓoye: data na Afirka daraja ce.
    """
    text = request.args.get("text", "").strip()
    language = request.args.get("lang", "ha").strip().lower()
    source = request.args.get("source", "api").strip().lower()

    if not text:
        return jsonify({
            "ok": False,
            "error": "Provide ?text=your text"
        }), 400
    if len(text) > 1000:
        return jsonify({
            "ok": False,
            "error": "Text too long (max 1000)"
        }), 400
    if language not in ("ha", "en", "fr", "ar", "yo", "ig", "sw", "dje", "ff", "pcm"):
        return jsonify({
            "ok": False,
            "error": "Unsupported language"
        }), 400

    # Ƙididdigar darajar data
    value_usd = 0.05
    if len(text) > 100:
        value_usd = 0.10
    if len(text) > 500:
        value_usd = 0.25

    try:
        with db_conn() as conn:
            conn.execute("""
                INSERT INTO data_bank
                (ts, text, language, source, value_usd)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat() + "Z",
                text[:1000], language, source, value_usd,
            ))
            total = conn.execute(
                "SELECT COUNT(*) as n FROM data_bank"
            ).fetchone()["n"]
            total_value = conn.execute(
                "SELECT COALESCE(SUM(value_usd), 0) as v FROM data_bank"
            ).fetchone()["v"]
    except sqlite3.Error as e:
        log_event("ERROR", f"data_collect: {e}")
        return jsonify({"ok": False, "error": "Database error"}), 500

    return jsonify({
        "ok": True,
        "message": "An tattara data ɗinka. Na gode!",
        "language": language,
        "value_usd": value_usd,
        "total_data": total,
        "total_value_usd": round(total_value, 2),
        "note": "Data ɗinka zai taimaka wajen gina AI ta Afirka",
        "built_by": "Sarki, Niamey",
    })


@app.route("/api/data/stats")
def data_stats():
    """Adadin data da aka tattara"""
    try:
        with db_conn() as conn:
            total = conn.execute(
                "SELECT COUNT(*) as n FROM data_bank"
            ).fetchone()["n"]
            total_value = conn.execute(
                "SELECT COALESCE(SUM(value_usd), 0) as v FROM data_bank"
            ).fetchone()["v"]

            by_lang = conn.execute("""
                SELECT language, COUNT(*) as n, SUM(value_usd) as v
                FROM data_bank
                GROUP BY language
                ORDER BY n DESC
            """).fetchall()

            by_source = conn.execute("""
                SELECT source, COUNT(*) as n
                FROM data_bank
                GROUP BY source
                ORDER BY n DESC
                LIMIT 10
            """).fetchall()
    except sqlite3.Error as e:
        log_event("ERROR", f"data_stats: {e}")
        return jsonify({"ok": False, "error": "Database error"}), 500

    return jsonify({
        "ok": True,
        "total_data": total,
        "total_value_usd": round(total_value, 2),
        "by_language": [dict(r) for r in by_lang],
        "by_source": [dict(r) for r in by_source],
        "note": "Data ɗin nan zai iya sayarwa ga Google, Meta, Microsoft",
        "price_range_usd": "$500 - $5,000 kowane ciniki",
        "built_by": "Sarki, Niamey",
    })


@app.route("/api/data/sell")
def data_sell():
    """
    Sayar da data ga companies.
    Sirrin da duniya ke ɓoye: data na Afirka.
    """
    language = request.args.get("lang", "ha").strip().lower()
    limit = request.args.get("limit", "100").strip()

    if not limit.isdigit():
        return jsonify({"ok": False, "error": "limit must be a number"}), 400

    limit = min(int(limit), 1000)

    try:
        with db_conn() as conn:
            rows = conn.execute("""
                SELECT ts, text, language, source, value_usd
                FROM data_bank
                WHERE language = ?
                ORDER BY id DESC
                LIMIT ?
            """, (language, limit)).fetchall()

            total_value = sum(r["value_usd"] for r in rows)
    except sqlite3.Error as e:
        log_event("ERROR", f"data_sell: {e}")
        return jsonify({"ok": False, "error": "Database error"}), 500

    return jsonify({
        "ok": True,
        "language": language,
        "count": len(rows),
        "total_value_usd": round(total_value, 2),
        "data": [dict(r) for r in rows],
        "note": "Wannan data za a iya sayarwa ga companies",
        "buyers": ["Google", "Meta", "Microsoft", "Jami'o'i", "Kamfanonin AI"],
        "price_range_usd": "$500 - $5,000",
        "built_by": "Sarki, Niamey",
    })


@app.route("/api/data/price")
def data_price():
    """
    Farashin data na Afirka — sirrin da duniya ke ɓoye.
    """
    return jsonify({
        "ok": True,
        "service": "AFRI-CORE Data Marketplace",
        "description": "Data na Afirka — don horar da AI",
        "sirrin": "Data ita ce zinariya ta sabon zamani",
        "prices": {
            "hausa": {
                "per_1000_sentences": "$500",
                "per_10000_sentences": "$4,500",
                "voice_hours": "$200/hour",
            },
            "yoruba": {
                "per_1000_sentences": "$600",
                "per_10000_sentences": "$5,000",
            },
            "igbo": {
                "per_1000_sentences": "$600",
                "per_10000_sentences": "$5,000",
            },
            "swahili": {
                "per_1000_sentences": "$500",
                "per_10000_sentences": "$4,000",
            },
            "zarma": {
                "per_1000_sentences": "$400",
            },
            "fulfulde": {
                "per_1000_sentences": "$500",
            },
        },
        "buyers": ["Google", "Meta", "Microsoft", "OpenAI", "Jami'o'i"],
        "why_valuable": "Babu data na Afirka a intanet — kowa yana nema",
        "why_hidden": "Kamfanonin fasaha suna ɓoye darajar data don su ci gajiyar Afirka",
        "built_by": "Sarki, Niamey",
    })# ============ CULTURE AI (Al'ada) ============

@app.route("/api/culture")
@rate_limit(30, 300)
def culture_info():
    """Al'adun Hausa — fasahar da duniya ke nema"""
    return jsonify({
        "ok": True,
        "service": "AFRI-CORE Culture AI",
        "version": "1000.0.0",
        "description": "Al'adun Hausa, Zarma, Yoruba, Igbo — da yadda ake magana",
        "categories": {
            "greetings": {
                "description": "Yadda ake gaisuwa a Hausa",
                "examples": [
                    {"hausa": "Sannu", "english": "Hello", "usage": "ga kowa"},
                    {"hausa": "Barka da safiya", "english": "Good morning", "usage": "da safe"},
                    {"hausa": "Barka da rana", "english": "Good afternoon", "usage": "da rana"},
                    {"hausa": "Barka da yamma", "english": "Good evening", "usage": "da yamma"},
                    {"hausa": "Sannu da zuwa", "english": "Welcome", "usage": "ga bako"},
                ],
            },
            "respect": {
                "description": "Matakan girmamawa a Hausa",
                "examples": [
                    {"hausa": "Ranki shi dade", "english": "May your soul live long", "usage": "ga sarki"},
                    {"hausa": "Ranka ya dade", "english": "Long live", "usage": "ga sarki"},
                    {"hausa": "Allah ya kiyaye", "english": "May God protect", "usage": "ga tsoho"},
                    {"hausa": "Allah ya sa albarka", "english": "May God bless", "usage": "ga kowa"},
                ],
            },
            "family": {
                "description": "Kalmomin iyali",
                "examples": [
                    {"hausa": "Uba", "english": "Father", "usage": "ga mahaifi"},
                    {"hausa": "Uwa", "english": "Mother", "usage": "ga mahaifiya"},
                    {"hausa": "Dan'uwa", "english": "Brother", "usage": "ga ɗan uwa"},
                    {"hausa": "Yar'uwa", "english": "Sister", "usage": "ga yar uwa"},
                ],
            },
            "market": {
                "description": "Kalmomin kasuwa",
                "examples": [
                    {"hausa": "Nawa ne?", "english": "How much?", "usage": "don tambaya"},
                    {"hausa": "Rage mini", "english": "Reduce for me", "usage": "don ciniki"},
                    {"hausa": "Na gode", "english": "Thank you", "usage": "bayan ciniki"},
                ],
            },
        },
        "built_by": "Sarki, Niamey",
    })


@app.route("/api/respect")
@rate_limit(30, 300)
def respect_levels():
    """Matakan girmamawa a Hausa"""
    return jsonify({
        "ok": True,
        "service": "AFRI-CORE Respect Levels",
        "levels": [
            {
                "level": "Sarki / King",
                "greeting": "Ranka ya dade",
                "english": "Long live the King",
                "usage": "ga sarki ko shugaba",
            },
            {
                "level": "Elder / Tsoho",
                "greeting": "Allah ya kiyaye",
                "english": "May God protect you",
                "usage": "ga tsoho ko dattijo",
            },
            {
                "level": "Parent / Iyaye",
                "greeting": "Barka da safiya",
                "english": "Good morning",
                "usage": "ga uba ko uwa",
            },
            {
                "level": "Friend / Aboki",
                "greeting": "Yaya dai",
                "english": "How are you?",
                "usage": "ga aboki",
            },
            {
                "level": "Child / Yaro",
                "greeting": "Sannu",
                "english": "Hello",
                "usage": "ga yaro",
            },
        ],
        "note": "Al'adar Hausa tana da matakan girmamawa daban-daban",
        "built_by": "Sarki, Niamey",
    })


@app.route("/api/proverb")
@rate_limit(30, 300)
def hausa_proverb():
    """Karin magana na Hausa"""
    proverbs = [
        {
            "hausa": "Komai nisan jifa, kasa zai dawo",
            "english": "However far a stone is thrown, it will return to the ground",
            "meaning": "Kowa zai dawo gida",
        },
        {
            "hausa": "Gaskiya ta fi kwabo",
            "english": "Truth is worth more than money",
            "meaning": "Gaskiya tana da daraja",
        },
        {
            "hausa": "Ilimi gishiri ne",
            "english": "Knowledge is salt",
            "meaning": "Ilimi yana da muhimmanci",
        },
        {
            "hausa": "Hakuri maganin duniya",
            "english": "Patience is the medicine of the world",
            "meaning": "Hakuri yana da muhimmanci",
        },
        {
            "hausa": "Kowa ya san gidan sarki, sarki ya san gidan kowa",
            "english": "Everyone knows the king's house, the king knows everyone's house",
            "meaning": "Sarki yana san kowa",
        },
        {
            "hausa": "Ruwa ba ya tsami ba",
            "english": "Water does not go sour",
            "meaning": "Abu mai kyau ba ya lalacewa",
        },
        {
            "hausa": "Dare daya ba ya ruwa",
            "english": "One night does not bring rain",
            "meaning": "Dole a yi hakuri",
        },
        {
            "hausa": "Sannu ba ta hana komai",
            "english": "Greeting does not prevent anything",
            "meaning": "Gaisuwa tana da muhimmanci",
        },
        {
            "hausa": "Kifi da ruwa, ruwa ne ya fi",
            "english": "Fish and water — water is greater",
            "meaning": "Muhimmin abu shi ne tushe",
        },
        {
            "hausa": "Idan ka ga gemun dan'uwanka ya kama wuta, ka jika naka",
            "english": "If you see your brother's beard on fire, wet yours",
            "meaning": "Taimaki ɗan'uwanka",
        },
    ]

    return jsonify({
        "ok": True,
        "service": "AFRI-CORE Proverbs",
        "count": len(proverbs),
        "proverb": random.choice(proverbs),
        "all": proverbs,
        "built_by": "Sarki, Niamey",
    })# ============ HARSUNAN AFRIKA 6 ============

AFRICAN_LANGUAGES = {
    "hausa": {"code": "ha", "speakers": "80M+", "region": "Nigeria, Niger, Ghana, Cameroon"},
    "yoruba": {"code": "yo", "speakers": "45M+", "region": "Southwest Nigeria, Benin"},
    "igbo": {"code": "ig", "speakers": "44M+", "region": "Southeast Nigeria"},
    "zarma": {"code": "dje", "speakers": "4M+", "region": "Niger, Mali, Burkina Faso"},
    "fulfulde": {"code": "ff", "speakers": "40M+", "region": "Sahel region"},
    "pidgin": {"code": "pcm", "speakers": "100M+", "region": "West Africa"},
}


@app.route("/api/v1000/translate/<lang>")
@rate_limit(30, 300)
def translate_african(lang):
    """Fassara zuwa harsunan Afirka 6"""
    text = request.args.get("text", "").strip()
    if not text:
        return jsonify({
            "ok": False,
            "error": f"Provide ?text=hello don {lang}"
        }), 400

    if lang not in AFRICAN_LANGUAGES:
        return jsonify({
            "ok": False,
            "error": "Unsupported language",
            "supported": list(AFRICAN_LANGUAGES.keys()),
        }), 400

    if lang == "hausa":
        lower = text.lower().strip()
        if lower in EN_HA:
            return jsonify({
                "ok": True,
                "language": "hausa",
                "code": "ha",
                "original": text,
                "translation": EN_HA[lower],
                "source": "AFRI-CORE-dictionary",
                "built_by": "Sarki, Niamey",
            })

    prompt = (
        f"Fassara wannan rubutun Turanci zuwa {lang.capitalize()} kawai. "
        f"Kada ka ƙara bayani. Rubutu: {text}"
    )
    ai_result, engine = ai_smart(prompt)
    if ai_result:
        return jsonify({
            "ok": True,
            "language": lang,
            "code": AFRICAN_LANGUAGES[lang]["code"],
            "original": text,
            "translation": ai_result,
            "source": f"AFRI-CORE-{engine}",
            "built_by": "Sarki, Niamey",
        })

    return jsonify({
        "ok": False,
        "error": "Translation temporarily unavailable",
    }), 503


@app.route("/api/v1000/languages")
def african_languages():
    """Harsunan Afirka da AFRI-CORE ke tallafa wa"""
    return jsonify({
        "ok": True,
        "service": "AFRI-CORE Languages",
        "count": 6,
        "languages": [
            {"name": "Hausa", **AFRICAN_LANGUAGES["hausa"]},
            {"name": "Yoruba", **AFRICAN_LANGUAGES["yoruba"]},
            {"name": "Igbo", **AFRICAN_LANGUAGES["igbo"]},
            {"name": "Zarma", **AFRICAN_LANGUAGES["zarma"]},
            {"name": "Fulfulde", **AFRICAN_LANGUAGES["fulfulde"]},
            {"name": "Pidgin", **AFRICAN_LANGUAGES["pidgin"]},
        ],
        "note": "Fasahar da duniya ke nema — babu a Afirka",
        "built_by": "Sarki, Niamey",
    })


# ============================================================
# XT9 ENGINE — SIRRIN DUNIYA
# Fasahar da babu a Afirka
# Sarki ne ya gina, Niamey, Niger
# ============================================================

class XT9Engine:
    """
    XT9 — Inji mai haɗa fasaha 9:
    1. Data Collection
    2. Algorithm
    3. AI (Groq + DeepSeek + Dictionary)
    4. Harsuna 6
    5. Voice AI
    6. Blockchain
    7. x402 Micropayments
    8. Data Marketplace
    9. Learning
    """

 VERSION = "1000.0.0"
