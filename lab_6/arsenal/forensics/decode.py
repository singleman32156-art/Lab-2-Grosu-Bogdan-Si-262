# -*- coding: utf-8 -*-
"""Decoder universal (Lucrarea 6, A1-A7).

Recunoaste stratul de codare (url / hex / base64), il desface in bucla,
sparge un XOR cu cheie de un octet si un hash de parola prin dictionar.

Folosire:
    python arsenal/forensics/decode.py "<sir>"
    python arsenal/forensics/decode.py probe/mesaj.txt --fisier
    python arsenal/forensics/decode.py probe/xor.bin --fisier --xor
    python arsenal/forensics/decode.py probe/hashuri.txt --fisier --hash --wordlist probe/wordlist.txt
"""
import argparse
import base64
import binascii
import hashlib
import json
import os
import re
from urllib.parse import unquote

CALE_FISA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fisa.json")


# ---------- A1. text si octeti ----------
def incalzire():
    s = "Salut"
    b = s.encode()
    print(b, b[0])                       # b'Salut' 83  (b[0] e un numar)
    h = b.hex()
    print(h, bytes.fromhex(h))           # 53616c7574 b'Salut'


# ---------- A2. recunoastere dupa forma ----------
def ghici_strat(s):
    """Clasifica sirul fara sa-l decodeze. Ordinea: url -> hex -> base64."""
    s = s.strip()
    if re.search(r"%[0-9a-fA-F]{2}", s):
        return "url"
    if re.fullmatch(r"[0-9a-fA-F]+", s) and len(s) % 2 == 0:
        return "hex"
    # base64: alfabetul A-Za-z0-9+/= si lungime multiplu de 4
    if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"


# ---------- A3. desfacerea unui strat ----------
def desfa(s):
    """Intoarce (strat, rezultat_bytes)."""
    strat = ghici_strat(s)
    try:
        if strat == "base64":
            return strat, base64.b64decode(s.strip(), validate=True)
        if strat == "hex":
            return strat, bytes.fromhex(s.strip())
        if strat == "url":
            return strat, unquote(s.strip()).encode()
    except (binascii.Error, ValueError):
        pass
    return "necunoscut", s.encode()


# ---------- A4. straturi multiple ----------
def citibil(b):
    """True daca toti octetii sunt imprimabili (32..126)."""
    return len(b) > 0 and all(32 <= c < 127 for c in b)


def desfa_tot(val, max_pasi=8):
    """Desface in bucla. Intoarce (lista_straturi, rezultat_final_bytes).

    Un strat intermediar (de ex. textul hex) este si el 'citibil', deci nu ne
    oprim la primul text citibil: ne oprim cand nu mai recunoastem un strat
    sau cand decodarea da octeti necitibili (atunci e probabil date, nu text).
    """
    straturi = []
    b = val.encode() if isinstance(val, str) else val
    for _ in range(max_pasi):
        if not citibil(b):
            break
        strat, nou = desfa(b.decode())
        if strat == "necunoscut":
            break
        straturi.append(strat)
        b = nou
    return straturi, b


# ---------- A5. XOR cu cheie de un octet ----------
def scor_text(b):
    """Cat de mult seamana cu text: procentul de litere, spatii si punctuatie
    obisnuita (cifrele si simbolurile rare nu conteaza ca "text")."""
    bun = sum(1 for c in b if chr(c).isalpha() or c in b" .,!?'-_{}")
    return bun / len(b)


def sparge_xor(date):
    """Incearca toate cele 256 de chei. Pastreaza rezultatele cu octeti
    imprimabili, ordonate dupa scor_text (cel mai bun primul).

    Filtrul simplu "toti octetii imprimabili" NU ajunge: o cheie care schimba
    doar biti de jos (0x81, 0x83...) lasa tot ASCII imprimabil, dar da
    gunoi. Scorul de text separa cheia buna de cele false.
    """
    gasite = []
    for k in range(256):
        clar = bytes(b ^ k for b in date)
        if citibil(clar):
            gasite.append((k, clar))
    gasite.sort(key=lambda kc: scor_text(kc[1]), reverse=True)
    return gasite


# ---------- A6. hash prin dictionar ----------
ALGO = {32: "md5", 40: "sha1", 64: "sha256"}


def sparge_hash(tinta, cai_wordlist):
    """Identifica algoritmul dupa lungime, apoi hashuieste fiecare cuvant."""
    tinta = tinta.strip().lower()
    algo = ALGO.get(len(tinta))
    if algo is None:
        return None, None
    with open(cai_wordlist, encoding="latin1") as f:
        for cuv in f:
            cuv = cuv.strip()
            if hashlib.new(algo, cuv.encode()).hexdigest() == tinta:
                return algo, cuv
    return algo, None


# ---------- A7. argparse + fisa JSON ----------
def salveaza_fisa(fisa, cale=CALE_FISA):
    with open(cale, "w", encoding="utf-8") as f:
        json.dump(fisa, f, ensure_ascii=False, indent=2)


def main():
    p = argparse.ArgumentParser(description="Decoder universal")
    p.add_argument("intrare", help="sir sau cale de fisier")
    p.add_argument("--fisier", action="store_true", help="intrarea e o cale")
    p.add_argument("--xor", action="store_true", help="sparge XOR cu cheie de un octet")
    p.add_argument("--hash", action="store_true", help="sparge hashurile din fisier")
    p.add_argument("--wordlist", default="probe/wordlist.txt")
    a = p.parse_args()

    fisa = {"intrare": a.intrare}

    if a.hash:
        rezultate = []
        for linie in open(a.intrare, encoding="utf-8"):
            if not linie.strip():
                continue
            algo, parola = sparge_hash(linie, a.wordlist)
            print(f"{linie.strip()}  {algo}  ->  {parola}")
            rezultate.append({"hash": linie.strip(), "algoritm": algo, "parola": parola})
        fisa.update(strat="hash", rezultat=rezultate)
    else:
        if a.fisier:
            date = open(a.intrare, "rb").read()
        else:
            date = a.intrare.encode()
        if a.xor:
            gasite = sparge_xor(date)
            print(f"{len(gasite)} chei dau octeti imprimabili; cea mai buna dupa scor:")
            for k, clar in gasite[:3]:
                print(f"cheie: {k} (0x{k:02x})  scor={scor_text(clar):.2f}  ->  {clar.decode()}")
            fisa.update(strat="xor", rezultat=[{"cheie": k, "clar": c.decode()} for k, c in gasite])
        else:
            straturi, b = desfa_tot(date.decode().strip())
            text = b.decode() if citibil(b) else b.hex()
            print("straturi:", " -> ".join(straturi) or "(niciunul)")
            print("rezultat:", text)
            fisa.update(strat=straturi, rezultat=text)

    salveaza_fisa(fisa)
    print("fisa salvata in", CALE_FISA)


if __name__ == "__main__":
    main()
