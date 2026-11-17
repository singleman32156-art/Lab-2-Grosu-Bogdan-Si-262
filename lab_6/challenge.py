# Varful salii: challenge.bin = base64( XOR_0x80( text ) ), cu md5 de verificat.
import hashlib
import re
from arsenal.forensics.decode import desfa, sparge_xor

brut = open("probe/challenge.bin").read().strip()
strat, dupa_b64 = desfa(brut)                      # pasul 1: stratul base64
print("1) strat:", strat, "->", dupa_b64)
k, clar = sparge_xor(dupa_b64)[0]                  # pasul 2: XOR brute force
print(f"2) XOR cheie {k} (0x{k:02x}) ->", clar.decode())
md5 = hashlib.md5(clar).hexdigest()                # pasul 3: verificare
asteptat = re.search(r"[0-9a-f]{32}", open("probe/challenge_hint.txt").read()).group()
print("3) md5:", md5, "| se potriveste cu hintul:", md5 == asteptat)
