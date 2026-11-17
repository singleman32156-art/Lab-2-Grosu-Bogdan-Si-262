# -*- coding: utf-8 -*-
"""Lucrarea 6, B1-B4: magic bytes, strings, EXIF/GPS, file carving.
Ruleaza din radacina depozitului:  python forensics.py
"""
import io
import re
import zipfile
from PIL import Image
from PIL.ExifTags import TAGS

SEMNATURI = [
    (b"%PDF", "pdf"),
    (b"\x89PNG", "png"),
    (b"\xff\xd8", "jpeg"),
    (b"PK\x03\x04", "zip/docx"),
]


# ---------- B1. magic bytes ----------
def tip_real(cale):
    with open(cale, "rb") as f:
        cap = f.read(8)
    for semn, nume in SEMNATURI:
        if cap.startswith(semn):
            return nume
    return cap.hex()


# ---------- B2. strings ----------
def strings(cale, minim=4):
    with open(cale, "rb") as f:
        date = f.read()
    return [m.decode() for m in re.findall(rb"[ -~]{%d,}" % minim, date)]


# ---------- B3. EXIF + GPS ----------
def grade_zecimale(dms, emisfera):
    g, m, s = (float(x) for x in dms)
    val = g + m / 60 + s / 3600
    return -val if emisfera in ("S", "W") else val


def exif_si_gps(cale):
    img = Image.open(cale)
    exif = img.getexif()
    meta = {TAGS.get(i, i): v for i, v in exif.items()}
    gps = exif.get_ifd(0x8825)            # blocul GPS (tag 34853)
    coord = None
    if gps:
        lat = grade_zecimale(gps[2], gps[1])
        lon = grade_zecimale(gps[4], gps[3])
        coord = (lat, lon)
    return meta, gps, coord


# ---------- B4. file carving ----------
def carving(cale, iesire="gasit.zip"):
    with open(cale, "rb") as f:
        date = f.read()
    i = date.find(b"PK\x03\x04")
    if i == -1:
        return None, None
    with open(iesire, "wb") as f:
        f.write(date[i:])
    with zipfile.ZipFile(io.BytesIO(date[i:])) as z:
        continut = {n: z.read(n).decode() for n in z.namelist()}
    return i, continut


if __name__ == "__main__":
    print("== B1. tip real ==")
    for f in ("foto.jpg", "ascuns.png", "xor.bin", "mesaj.txt"):
        print(f"  probe/{f:12s} -> {tip_real('probe/' + f)}")

    print("\n== B2. strings (ascuns.png, doar secventele relevante) ==")
    for s in strings("probe/ascuns.png"):
        print("  ", s)

    print("\n== B3. EXIF / GPS (foto.jpg) ==")
    meta, gps, coord = exif_si_gps("probe/foto.jpg")
    for k, v in meta.items():
        print(f"  {k} = {v}")
    print("  GPS brut:", dict(gps))
    print("  GPS zecimal: lat={:.6f}, lon={:.6f}".format(*coord))

    print("\n== B4. file carving (ascuns.png) ==")
    i, continut = carving("probe/ascuns.png")
    print("  arhiva extrasa de la octetul", i)
    for nume, text in continut.items():
        print(f"  {nume}: {text.strip()}")
