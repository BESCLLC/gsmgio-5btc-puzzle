"""Test the issue-#69 'master key' exhaustively against both blobs.

818af53d... is arithmetically what the issue says it is -- but confirming an
author's own arithmetic is not evidence, and XOR-ing the SHA-256 of seven tokens
where one appears twice means the key carries no information from that token at
all. What matters is whether it decrypts. So: as a passphrase in every form, and
injected directly as the AES key against every IV the format could plausibly
supply.
"""
import hashlib
from Crypto.Cipher import AES
from gsmg import Blob, evp_bytes_to_key
from pagehash import BLOBS
import validate

MK_HEX = "818af53daa3028449f125a2e4f47259ddf9b9d86e59ce6c4993a67ffd76bb402"
MK = bytes.fromhex(MK_HEX)
PRINTABLE = set(range(32, 127)) | {9, 10, 13}


def looks_like_text(pt):
    return pt and sum(b in PRINTABLE for b in pt) / len(pt) > 0.85


n = hits = 0
for bname, blob in BLOBS.items():
    print(f"\n=== {bname} (salt {blob.salt.hex()}, {len(blob.ct)} bytes) ===")

    # 1. as a passphrase, every representation, every KDF
    for pwname, pw in (("hex-lower", MK_HEX), ("hex-upper", MK_HEX.upper()),
                       ("raw-bytes", MK.decode("latin-1")),
                       ("sha256(hex)", hashlib.sha256(MK_HEX.encode()).hexdigest()),
                       ("sha256(raw)", hashlib.sha256(MK).hexdigest())):
        for md in ("sha256", "md5"):
            n += 1
            pt = blob.decrypt(pw, md)
            ok = looks_like_text(pt)
            print(f"  pass={pwname:12s} kdf={md:6s} -> "
                  f"{'TEXT!' if ok else ('valid padding, binary' if pt else 'fails padding')}")
            if ok:
                hits += 1
                print(f"      {pt[:200]!r}")

    # 2. direct key injection, every IV the format could supply
    ivs = {
        "zero": bytes(16),
        "salt*2": blob.salt * 2,
        "salt+zero": blob.salt + bytes(8),
        "zero+salt": bytes(8) + blob.salt,
        "key[:16]": MK[:16],
        "key[16:]": MK[16:],
        "sha256(key)[:16]": hashlib.sha256(MK).digest()[:16],
        "md5(key)": hashlib.md5(MK).digest(),
        "evp-iv-sha256": evp_bytes_to_key(MK_HEX, blob.salt, "sha256")[1],
        "evp-iv-md5": evp_bytes_to_key(MK_HEX, blob.salt, "md5")[1],
        "ct[:16]": blob.ct[:16],
    }
    for ivname, iv in ivs.items():
        n += 1
        pt = AES.new(MK, AES.MODE_CBC, iv).decrypt(blob.ct)
        pad = pt[-1]
        valid = 0 < pad <= 16 and pt[-pad:] == bytes([pad]) * pad
        body = pt[:-pad] if valid else pt
        ok = looks_like_text(body)
        print(f"  -K key iv={ivname:16s} -> padding {'ok ' if valid else 'BAD'} | "
              f"printable {sum(b in PRINTABLE for b in body)/len(body):.0%}"
              f"{'  <-- TEXT!' if ok else ''}")
        if ok:
            hits += 1
            print(f"      {body[:200]!r}")
            for key, addr in validate.check(body):
                print(f"      *** PRIZE ADDRESS {addr} <- {key}")

print(f"\n{n} decryption attempts with the issue-#69 master key, {hits} produced text")
