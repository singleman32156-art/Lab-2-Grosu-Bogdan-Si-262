# Raport

**Student:** Grosu Bogdan, grupa SI 262
**Disciplina:** Tehnici de programare (UTM · FCIM · Securitate informațională)

## Laboratorul 6. Informații invizibile: forensics și steganografie

Toate țintele au fost generate local cu `probe/pregateste.py`. Comenzi rulate din rădăcina depozitului.

### Lucrarea A. Decoderul universal (`arsenal/forensics/decode.py`)

**Mesajul cu straturi (`probe/mesaj.txt`).** Decoderul a recunoscut și desfăcut trei straturi, în ordinea
`base64 → base64 → hex`, iar la capăt a rămas textul clar **`FLAG{straturi_de_encoding}`**.
Bucla nu se oprește la primul text „citibil”: și textul hex, și cel base64 intermediar sunt făcute din
caractere imprimabile. Se oprește abia când șirul nu mai are forma niciunui strat cunoscut.

**XOR cu cheie de un octet (`probe/xor.bin`).** Brute force pe cele 256 de chei. Cheia corectă este **128 (0x80)**,
iar textul este `Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}`.
Filtrul simplu „toți octeții imprimabili” lasă 17 chei candidate, nu una singură, pentru că o cheie care
modifică doar biții de jos (0x81, 0x83 etc.) păstrează tot ASCII imprimabil. Am adăugat un scor
(procentul de litere, spații și punctuație uzuală, inclusiv `_{}` din formatul flag-urilor) și cheia 0x80 iese prima, cu scor 1.00 față de 0.88 pentru a doua.
Prima variantă a scorului număra și cifrele și alegea o cheie falsă (0x97); am corectat-o după ce am văzut rezultatul.

**Hash-uri prin dicționar (`probe/hashuri.txt`).** Toate au 32 de caractere hex, deci MD5. Atac cu
`probe/wordlist.txt`, hashuind fiecare cuvânt și comparând:

| hash (MD5) | parola |
|---|---|
| 5f4dcc3b5aa765d61d8327deb882cf99 | password |
| 8621ffdbc5698829397d97767ac13db3 | dragon |
| d8578edf8458ce06fbc5bb76a58c5ca4 | qwerty |
| 0d107d09f5bbe40cade3de5c71e9e9b7 | letmein |
| d0763edaa9d9bd2a9516280e9044d885 | monkey |

Un hash nu se „decriptează”: parolele sunt slabe și apar într-o listă de cuvinte uzuale, de aceea cad imediat.

**Fișa și testul.** `fisa.json` păstrează rezultatul ultimei rulări (mesajul cu straturi). Testele din
`teste/test_decode.py` trec: `5 passed`.

### Lucrarea B. Forensics pe fișiere și steganografie

**B1. Tipul real (magic bytes).**

| fișier | primii octeți | tip real |
|---|---|---|
| `foto.jpg` | `ff d8` | JPEG |
| `ascuns.png` | `89 50 4e 47` | PNG |
| `xor.bin`, `mesaj.txt` | niciuna din semnăturile cunoscute | date brute / text, nu un format de fișier |

**B2. strings.** În `ascuns.png`, pe lângă marcajele PNG (`IHDR`, `IDATx`, `IEND`), apare după `IEND`
șirul `secret.txt` și `FLAG{ascuns_prin_carving}`. Este un indiciu clar că la coadă este lipit un alt fișier.

**B3. Metadate EXIF și GPS (`foto.jpg`).** Producător Apple, model iPhone 13, data `2026:09:14 10:30:00`.
Blocul GPS: `N 47°1′0″`, `E 28°51′27″`, adică în grade zecimale **47.016667 N, 28.857500 E**
(zona Chișinăului). Din asta se vede de ce valorează EXIF pentru OSINT și de ce se șterge înainte de publicare.

**B4. File carving (`ascuns.png`).** Semnătura `PK\x03\x04` a fost găsită la octetul **782**, imediat după
sfârșitul real al PNG-ului. Din acel octet până la capăt am salvat `gasit.zip`. Arhiva conține
`secret.txt` cu textul **`FLAG{ascuns_prin_carving}`**.

**B5–B6. Steganografie LSB (`stego.py`, `stego.png`).** Mesajul `FLAG{ascuns_in_pixeli}` (plus un octet 0 ca
marcaj de final) a fost scris, câte un bit, în ultimul bit al canalelor R, G, B ale pixelilor din `foto.jpg`.
Imaginea s-a salvat în PNG, fără pierderi (un JPG ar fi recomprimat și ar fi distrus biții). Diferența maximă față
de original este 1 pe canal, deci imaginea arată identic. Dezvăluirea citește ultimii biți, îi grupează câte 8 și
se oprește la primul octet 0. Mesajul revelat: **`FLAG{ascuns_in_pixeli}`**.

### Vârful sălii (`challenge.py`)

`challenge.bin` = base64 peste XOR cu un octet. Pașii:
1. strat `base64` desfăcut cu `desfa()`;
2. XOR spart cu `sparge_xor()`: cheia **0x80**, text **`FLAG{lant_complet_despicat}`**;
3. verificare: md5 al textului clar coincide cu cel din `challenge_hint.txt`.

### Cadrul legal

Toate analizele s-au făcut doar pe fișierele generate local pentru laborator, nu pe date ale altor persoane.

