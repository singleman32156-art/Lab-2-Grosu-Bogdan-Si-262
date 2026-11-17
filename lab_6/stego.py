# -*- coding: utf-8 -*-
"""Lucrarea 6, B5-B6: steganografie LSB (ascunde / dezvaluie).
    python stego.py            -> ascunde in stego.png si apoi dezvaluie
"""
from PIL import Image


def ascunde(cale_gazda, mesaj, cale_iesire="stego.png"):
    img = Image.open(cale_gazda).convert("RGB")
    px = list(img.getdata())
    # mesajul + un octet 0 la final, ca marcaj de sfarsit
    biti = "".join(f"{x:08b}" for x in mesaj + b"\x00")
    if len(biti) > len(px) * 3:
        raise ValueError("mesajul nu incape in imagine")
    nou, k = [], 0
    for (r, g, b) in px:
        canale = [r, g, b]
        for c in range(3):
            if k < len(biti):
                canale[c] = (canale[c] & ~1) | int(biti[k])
                k += 1
        nou.append(tuple(canale))
    img.putdata(nou)
    img.save(cale_iesire, format="PNG")   # PNG = fara pierderi; JPG ar distruge bitii
    return cale_iesire


def dezvaluie(cale):
    px = list(Image.open(cale).convert("RGB").getdata())
    biti = ""
    for (r, g, b) in px:
        biti += f"{r & 1}{g & 1}{b & 1}"
    octeti = bytearray()
    for i in range(0, len(biti) - 7, 8):
        o = int(biti[i:i + 8], 2)
        if o == 0:                        # primul octet 0 = final de mesaj
            break
        octeti.append(o)
    return bytes(octeti)


if __name__ == "__main__":
    mesaj = b"FLAG{ascuns_in_pixeli}"
    print("ascuns in:", ascunde("probe/foto.jpg", mesaj))
    print("dezvaluit:", dezvaluie("stego.png").decode())
