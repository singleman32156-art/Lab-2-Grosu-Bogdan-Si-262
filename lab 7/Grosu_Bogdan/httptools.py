"""httptools.py - Trusa de unelte HTTP (Grosu Bogdan, SI 262)

Funcții care vorbesc cu un server web folosind biblioteca requests.
Toate cererile merg la httpbin.org; adresa se schimbă doar în BASE.
"""
import requests

BASE = "https://httpbin.org"
PATHS = ["/get", "/redirect/2", "/delay/1", "/status/404", "/delay/5"]
TIMEOUT = 3  # secunde; nicio cerere nu așteaptă mai mult de atât


# Partea 1: parametri în URL
def search(params):
    """GET pe /get cu parametri în URL; returnează parametrii primiți de server."""
    r = requests.get(BASE + "/get", params=params, timeout=TIMEOUT)
    return r.json()["args"]


def search_url(params):
    """Returnează adresa completă construită de requests, cu tot cu parametri."""
    r = requests.get(BASE + "/get", params=params, timeout=TIMEOUT)
    return r.url


# Partea 2: anteturi
def fetch_with_agent(agent):
    """GET pe /headers cu User-Agent=agent; returnează User-Agent-ul văzut de server."""
    r = requests.get(BASE + "/headers", headers={"User-Agent": agent}, timeout=TIMEOUT)
    return r.json()["headers"]["User-Agent"]


def default_agent():
    """Returnează User-Agent-ul trimis de requests când nu setezi nimic."""
    r = requests.get(BASE + "/headers", timeout=TIMEOUT)
    return r.json()["headers"]["User-Agent"]


# Partea 3: trimiterea datelor
def post_json(data):
    """POST cu datele ca JSON pe /post; returnează JSON-ul primit de server."""
    r = requests.post(BASE + "/post", json=data, timeout=TIMEOUT)
    return r.json()["json"]


def post_form(data):
    """POST cu datele ca formular pe /post; returnează formularul primit de server."""
    r = requests.post(BASE + "/post", data=data, timeout=TIMEOUT)
    return r.json()["form"]


# Partea 4: coduri de stare
def describe_status(code):
    """GET pe /status/<code>; returnează 'succes', 'eroare client' sau 'eroare server'."""
    try:
        # allow_redirects=False: vrem codul cerut, nu pe cel de după o redirecționare
        r = requests.get(f"{BASE}/status/{code}", timeout=TIMEOUT, allow_redirects=False)
    except requests.RequestException:
        return "eroare de rețea"
    if 200 <= r.status_code < 300:
        return "succes"
    if 400 <= r.status_code < 500:
        return "eroare client"
    if 500 <= r.status_code < 600:
        return "eroare server"
    return "alt cod"  # 1xx / 3xx nu sunt cerute de enunț


def is_ok(code):
    """GET pe /status/<code>; True dacă cererea a reușit, altfel False."""
    try:
        r = requests.get(f"{BASE}/status/{code}", timeout=TIMEOUT)
        r.raise_for_status()  # ridică HTTPError la 4xx și 5xx
        return True
    except requests.RequestException:  # include HTTPError, timeout, fără conexiune
        return False


# Partea 5: redirecționări
def count_redirects(n):
    """GET pe /redirect/<n>; returnează câte redirecționări au fost urmate."""
    r = requests.get(f"{BASE}/redirect/{n}", timeout=TIMEOUT)
    return len(r.history)


def final_url(n):
    """GET pe /redirect/<n>; returnează adresa la care ai ajuns."""
    r = requests.get(f"{BASE}/redirect/{n}", timeout=TIMEOUT)
    return r.url


def first_hop(n):
    """GET pe /redirect/<n> FĂRĂ a urma redirecționarea; returnează antetul Location."""
    r = requests.get(f"{BASE}/redirect/{n}", timeout=TIMEOUT, allow_redirects=False)
    return r.headers["Location"]


# Partea 6: sesiuni și cookie-uri
def cookie_demo(name, value):
    """Setează un cookie, apoi citește cookie-urile înapoi cu O SINGURĂ sesiune."""
    with requests.Session() as s:
        # params= codifică corect numele/valoarea în adresă
        s.get(BASE + "/cookies/set", params={name: value}, timeout=TIMEOUT)
        r = s.get(BASE + "/cookies", timeout=TIMEOUT)
        return r.json()["cookies"]


def no_session_demo(name, value):
    """Același lucru cu apeluri simple requests.get; returnează cookie-urile văzute de server.
    Rezultatul e {} pentru că fiecare apel simplu uită cookie-ul."""
    requests.get(BASE + "/cookies/set", params={name: value}, timeout=TIMEOUT)
    r = requests.get(BASE + "/cookies", timeout=TIMEOUT)
    return r.json()["cookies"]


# Partea 7: raportul final
def report(path):
    """Returnează un dicționar care descrie pagina de la BASE + path.
    Nu se oprește niciodată cu eroare."""
    try:
        r = requests.get(BASE + path, timeout=TIMEOUT)
    except requests.RequestException as e:
        # mesaj scurt: doar numele erorii (Timeout, ConnectionError etc.)
        return {"status": None, "error": type(e).__name__}
    return {
        "status": r.status_code,
        "final_url": r.url,
        "redirects": len(r.history),
        "seconds": round(r.elapsed.total_seconds(), 2),
        "content_type": r.headers.get("Content-Type"),
    }


def main():
    # 1. un raport pentru fiecare adresă, cu adresa păstrată în dicționar
    results = []
    for path in PATHS:
        info = report(path)
        info["path"] = path
        results.append(info)

    # 2. doar paginile cu status 200, cea mai lentă prima
    ok_pages = [p for p in results if p["status"] == 200]
    ok_pages.sort(key=lambda p: p["seconds"], reverse=True)
    for p in ok_pages:
        print(f"{p['path']} -> {p['status']}, {p['seconds']} secunde")

    # 3. totaluri (404 și timeout-ul se numără ca eșuate)
    print(f"Reușite: {len(ok_pages)} | Eșuate: {len(results) - len(ok_pages)}")


# Bonus: autentificare
def check_login(user, password):
    """True dacă serverul acceptă datele de autentificare, altfel False."""
    try:
        r = requests.get(
            BASE + "/basic-auth/admin/secret",
            auth=(user, password),
            timeout=TIMEOUT,
        )
    except (requests.RequestException, UnicodeError):
        # UnicodeError: Basic auth codifică în latin-1, iar "ș" din "greșit" nu încape
        return False
    return r.status_code == 200


if __name__ == "__main__":
    main()
