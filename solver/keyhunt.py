"""A and C as KEY MATERIAL, not text.

The entropy bound rules out A/C bijectively decoding to English -- 262 bits into
36 bytes cannot be 36 English characters. It says nothing against them decoding
to a KEY: 32 bytes of AES key is supposed to be ~8 bits/byte. Testing these runs
for readable output was testing for the wrong thing.

Direct key injection needs no IV guess for the rejection test: in CBC the final
block decrypts as D(C_n) XOR C_{n-1}, which never touches the IV. So the PKCS#7
oracle is IV-independent, and one AES block operation per candidate covers it.
"""
import itertools, sys, time, base64
from Crypto.Cipher import AES
from pagehash import BLOBS

LETTERS = "abcdefghi"
b45 = base64.b64decode("U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46z"
                       "gKlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4")
BLOBLIST = [("sal", BLOBS["salphaseion"].ct), ("cos", BLOBS["cosmic"].ct),
            ("b45", b45[16:])]


def pad_ok(key, ct):
    """IV-independent PKCS#7 check on the final block."""
    tail = AES.new(key, AES.MODE_ECB).decrypt(ct[-16:])
    prev = ct[-32:-16]
    p = tail[-1] ^ prev[-1]
    if p == 0 or p > 16:
        return False
    return bytes(a ^ b for a, b in zip(tail, prev))[-p:] == bytes([p]) * p


def decode(s, mapping):
    n = 0
    for c in s:
        n = n * 10 + mapping[c]
    h = f"{n:x}"
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h)
    except ValueError:
        return b""


def hunt(name, s):
    t0 = time.time(); n = 0; hits = []
    for digits in ("123456789", "012345678"):
        for perm in itertools.permutations(digits):
            m = dict(zip(LETTERS, [int(d) for d in perm]))
            bs = decode(s, m)
            if len(bs) < 32:
                continue
            # every 32-byte window of the decoded payload
            for off in range(0, len(bs) - 31):
                key = bs[off:off + 32]
                for bn, ct in BLOBLIST:
                    n += 1
                    if pad_ok(key, ct):
                        hits.append((bn, ''.join(perm), off, key.hex()))
                        print(f"  PAD OK blob={bn} map={''.join(perm)} off={off} "
                              f"key={key.hex()}", flush=True)
    print(f"[{name}] {n:,} key trials in {time.time()-t0:.0f}s, "
          f"{len(hits)} padding-valid (~{n/256:.0f} by chance)")
    return hits


if __name__ == "__main__":
    A = open("partA.txt").read().strip()
    hunt("partA", A)
