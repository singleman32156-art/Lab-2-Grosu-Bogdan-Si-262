import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]  # [cite: 18]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]  # [cite: 18]


# Partea 1: Funcții[cite: 12]
def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    if not path.startswith("/"):
        path = "/" + path
    return f"https://{host}{path}"


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    return url.startswith("https://")


# Partea 2: Trimiterea unei cereri[cite: 13]
def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        r = requests.get(url, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type', 'unknown')}")
    except requests.RequestException as e:
        print(f"Eroare conexiune: {str(e)}")


# Partea 3: Un verificator reutilizabil[cite: 13]
def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        r = requests.get(url, timeout=5)
        return {
            "status": r.status_code,
            "content_type": r.headers.get("Content-Type", "unknown"),
            "length": len(r.content),
            "server": r.headers.get("Server", "unknown")
        }
    except requests.RequestException:
        return {"status": None, "error": "Conexiune eșuată sau timeout"}


# Partea 4: Verificarea mai multor site-uri[cite: 13]
def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    rezultate = []

    # 1. Apelează check_site pentru fiecare adresă
    for url in SITES:
        rez = check_site(url)
        rez["url"] = url
        rezultate.append(rez)

    # 2. Afișează doar site-urile care au returnat 200
    reusite = [r for r in rezultate if r["status"] == 200]

    # 3. Sortează-le după length descrescător
    reusite.sort(key=lambda x: x.get("length", 0), reverse=True)

    for r in reusite:
        print(f"{r['url']} -> {r['status']}, {r['length']} octeți")

    # 4. Afișează rezumatul la final
    total_reusite = len(reusite)
    total_esuate = len(rezultate) - total_reusite
    print(f"Reușite: {total_reusite} | Eșuate: {total_esuate}")


# Partea 5: Audit de securitate[cite: 14]
def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    try:
        r = requests.get(url, timeout=5)
        # Transformăm anteturile primite în litere mici pentru comparație (cazul nu contează)[cite: 15]
        headers_lower = {k.lower(): v for k, v in r.headers.items()}

        present = []
        missing = []

        for h in SECURITY_HEADERS:
            if h.lower() in headers_lower:
                present.append(h)
            else:
                missing.append(h)

        score = int((len(present) / len(SECURITY_HEADERS)) * 100)
        return {"present": present, "missing": missing, "score": score}

    except requests.RequestException:
        return {"status": None, "error": "Conexiune eșuată sau timeout"}


# Partea 6: Încercări repetate[cite: 15]
def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    last_status = None
    last_error = None

    for i in range(1, attempts + 1):
        try:
            r = requests.get(url, timeout=5)
            last_status = r.status_code

            # Ne oprim imediat dacă statusul e sub 500 (inclusiv erori 4xx)[cite: 15]
            if r.status_code < 500:
                return {"status": r.status_code, "attempts": i}

        except requests.RequestException as e:
            last_status = None
            last_error = str(e)

    # Dacă ajungem aici, înseamnă că toate încercările au eșuat (fie 5xx repetat, fie conexiune picată)
    rezultat = {"status": last_status, "attempts": attempts}
    if last_status is None:
        rezultat["error"] = "Conexiune eșuată la toate încercările"

    return rezultat
