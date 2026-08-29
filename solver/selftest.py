"""Prove the KDF + oracle against real openssl output before trusting a sweep."""
import base64, subprocess, sys
from gsmg import Blob, evp_bytes_to_key

ok = True
for md in ("md5", "sha256"):
    pw = "causality"
    msg = b"the quick brown fox jumps over the lazy dog 0123456789 abcdefgh"
    enc = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-a", "-A", "-md", md, "-pass", "pass:" + pw],
        input=msg, capture_output=True, check=True).stdout.decode().strip()
    b = Blob(enc)
    got = b.check(pw, md)
    print(f"[{md}] roundtrip:", "PASS" if got == msg else f"FAIL {got!r}")
    ok &= got == msg
    print(f"[{md}] wrong pw rejected:", "PASS" if b.check("nope", md) is None else "FAIL")

sys.exit(0 if ok else 1)
