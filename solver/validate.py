"""Turn a candidate plaintext into a verdict.

A sweep hit is only interesting if the bytes are a private key for one of the
prize addresses, so decide that here instead of eyeballing plaintexts. Pure
Python secp256k1 -- it runs once per hit, not once per candidate, so speed is
irrelevant.
"""
import hashlib
import re

PRIZE = {
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",   # the 5 BTC address
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",   # the second, larger-funded address
}

P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    if p[0] == q[0] and (p[1] + q[1]) % P == 0:
        return None
    if p == q:
        l = 3 * p[0] * p[0] * pow(2 * p[1], P - 2, P) % P
    else:
        l = (q[1] - p[1]) * pow(q[0] - p[0], P - 2, P) % P
    x = (l * l - p[0] - q[0]) % P
    return (x, (l * (p[0] - x) - p[1]) % P)


def _mul(k, p=G):
    r = None
    while k:
        if k & 1:
            r = _add(r, p)
        p = _add(p, p)
        k >>= 1
    return r


def b58check(payload):
    chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    n = int.from_bytes(payload + chk, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = B58[r] + out
    return "1" * (len(payload + chk) - len((payload + chk).lstrip(b"\0"))) + out


def addresses(priv_int):
    """Both the compressed and uncompressed P2PKH addresses for a key."""
    if not 0 < priv_int < N:
        return []
    x, y = _mul(priv_int)
    forms = [b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big"),
             bytes([2 + (y & 1)]) + x.to_bytes(32, "big")]
    out = []
    for pub in forms:
        h = hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()
        out.append(b58check(b"\x00" + h))
    return out


def keys_in(pt):
    """Every plausible private key encoding inside a candidate plaintext."""
    found = []
    if isinstance(pt, bytes):
        text = pt.decode("latin-1")
        if len(pt) == 32:
            found.append(int.from_bytes(pt, "big"))
    else:
        text = pt
    for m in re.finditer(r"[0-9a-fA-F]{64}", text):
        found.append(int(m.group(), 16))
    for m in re.finditer(r"[5KL][1-9A-HJ-NP-Za-km-z]{50,51}", text):
        n = 0
        for ch in m.group():
            n = n * 58 + B58.index(ch)
        raw = n.to_bytes(37 + (len(m.group()) == 52), "big")
        found.append(int.from_bytes(raw[1:33], "big"))
    return found


def check(pt):
    """-> list of (key, address) that actually hit a prize address."""
    hits = []
    for k in keys_in(pt):
        for a in addresses(k):
            if a in PRIZE:
                hits.append((f"{k:064x}", a))
    return hits


if __name__ == "__main__":
    # sanity: a known key/address pair, then the real prize addresses must not
    # be reachable from anything we have.
    k = 1
    print("privkey 1 ->", addresses(k))
    assert addresses(1)[0] == "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm", "secp256k1 broken"
    assert addresses(1)[1] == "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH", "compressed broken"
    print("secp256k1 + base58 self-test: PASS")
    print("prize addresses watched:", sorted(PRIZE))
