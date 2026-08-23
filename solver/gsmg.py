"""Core primitives for attacking the GSMG.IO 5 BTC puzzle end-game blobs.

Everything here is deliberately dependency-light: pycryptodome for AES, hashlib
for the digests, and a hand-rolled EVP_BytesToKey so we can reproduce exactly
what `openssl enc -aes-256-cbc -a -pass pass:...` did in 2019 (MD5 KDF) and what
a modern OpenSSL 1.1+ would do (SHA-256 KDF).
"""
import base64
import hashlib
from Crypto.Cipher import AES

# ---------------------------------------------------------------- ciphertexts

# SalPhaseIon page, the small blob. The two 64-char base64 runs printed on the
# page are interleaved with the "abba" bits that spell "enter"; stripped and
# rejoined they are one 96-byte OpenSSL "Salted__" container:
#   8 byte magic + 8 byte salt + 80 byte ciphertext (5 AES blocks).
SALPHASEION_B64 = (
    "U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z"
    "QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ"
)


def load_blob(b64):
    raw = base64.b64decode(b64)
    assert raw[:8] == b"Salted__", "not an OpenSSL salted container"
    return raw[8:16], raw[16:]


# ------------------------------------------------------------------- key derivation

def evp_bytes_to_key(password, salt, digest="md5", key_len=32, iv_len=16):
    """OpenSSL EVP_BytesToKey with count=1 (what `enc` uses)."""
    if isinstance(password, str):
        password = password.encode()
    d = b""
    prev = b""
    while len(d) < key_len + iv_len:
        prev = hashlib.new(digest, prev + password + salt).digest()
        d += prev
    return d[:key_len], d[key_len:key_len + iv_len]


# ------------------------------------------------------------------- fast oracle

class Blob:
    """Wraps one salted blob and answers 'could this password be right?' cheaply.

    A wrong AES-256-CBC password leaves random bytes in the final block, so valid
    PKCS#7 padding survives with probability ~1/256 (a bit more, counting the
    multi-byte pad values). We therefore only need the *last* ciphertext block
    and the one before it to reject a candidate: one AES block decryption instead
    of decrypting the whole message.
    """

    def __init__(self, b64):
        self.salt, self.ct = load_blob(b64)
        assert len(self.ct) % 16 == 0 and len(self.ct) >= 32
        self.last = self.ct[-16:]
        self.prev = self.ct[-32:-16]

    def check(self, password, digest="md5"):
        key, _iv = evp_bytes_to_key(password, self.salt, digest)
        tail = AES.new(key, AES.MODE_ECB).decrypt(self.last)
        pad = tail[-1] ^ self.prev[-1]
        if pad == 0 or pad > 16:
            return None
        plain_tail = bytes(a ^ b for a, b in zip(tail, self.prev))
        if plain_tail[-pad:] != bytes([pad]) * pad:
            return None
        return self.decrypt(password, digest)

    def check_key(self, key, iv):
        """Direct key/IV injection (`openssl enc -K ... -iv ...`)."""
        pt = AES.new(key, AES.MODE_CBC, iv).decrypt(self.ct)
        pad = pt[-1]
        if pad == 0 or pad > 16 or pt[-pad:] != bytes([pad]) * pad:
            return None
        return pt[:-pad]

    def decrypt(self, password, digest="md5"):
        key, iv = evp_bytes_to_key(password, self.salt, digest)
        pt = AES.new(key, AES.MODE_CBC, iv).decrypt(self.ct)
        pad = pt[-1]
        if pad == 0 or pad > 16 or pt[-pad:] != bytes([pad]) * pad:
            return None
        return pt[:-pad]


def sha256hex(s):
    if isinstance(s, str):
        s = s.encode()
    return hashlib.sha256(s).hexdigest()
