import hashlib
from arsenal.forensics.decode import (
    ghici_strat, desfa, desfa_tot, sparge_xor, sparge_hash,
)


def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_ghici_ordinea():
    assert ghici_strat("%2Fetc") == "url"
    assert ghici_strat("48656c6c6f") == "hex"
    assert ghici_strat("U2FsdXQ=") == "base64"
    assert ghici_strat("FLAG{x}") == "necunoscut"


def test_straturi_multiple():
    # base64(base64(hex("Salut")))
    import base64
    val = base64.b64encode(base64.b64encode(b"Salut".hex().encode())).decode()
    straturi, b = desfa_tot(val)
    assert straturi == ["base64", "base64", "hex"]
    assert b == b"Salut"


def test_xor_un_octet():
    date = bytes(c ^ 0x80 for c in b"mesaj secret")
    assert sparge_xor(date)[0] == (0x80, b"mesaj secret")


def test_hash_dictionar(tmp_path):
    w = tmp_path / "w.txt"
    w.write_text("abc\ndragon\nzzz\n")
    h = hashlib.md5(b"dragon").hexdigest()
    assert sparge_hash(h, str(w)) == ("md5", "dragon")
