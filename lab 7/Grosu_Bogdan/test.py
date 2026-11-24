"""test.py - apeluri de verificare pentru httptools.py (Grosu Bogdan, SI 262)

Rulare: python test.py
Fiecare linie afișează rezultatul unei funcții; rezultatele așteptate sunt în enunț,
la secțiunea "Exemple pentru testare". Rularea durează câteva secunde (/delay/1, /delay/5).
"""
from httptools import *

# Partea 1: parametri în URL
print(search({"q": "python", "page": "2"}))
print(search({"q": "hello world & co"}))
print(search_url({"q": "python", "page": "2"}))

# Partea 2: anteturi
print(fetch_with_agent("MyBot/1.0"))
print(default_agent())

# Partea 3: trimiterea datelor
print(post_json({"name": "Ana", "age": 19, "tags": ["a", "b"]}))
print(post_form({"user": "ana", "city": "Bălți"}))

# Partea 4: coduri de stare
print(describe_status(200), describe_status(404), describe_status(503))
print(is_ok(204), is_ok(500))

# Partea 5: redirecționări
print(count_redirects(3), final_url(2), first_hop(3))

# Partea 6: sesiuni și cookie-uri
print(cookie_demo("theme", "dark"))
print(no_session_demo("theme", "dark"))  # {} : fără sesiune, cookie-ul se pierde

# Partea 7: raportul final
print(report("/get"))
print(report("/redirect/2"))
print(report("/delay/1"))
print(report("/delay/5"))  # ReadTimeout după ~3 secunde

# Bonus: autentificare
print(check_login("admin", "secret"), check_login("admin", "greșit"))
