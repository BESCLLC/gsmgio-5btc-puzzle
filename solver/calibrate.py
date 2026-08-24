"""Verify the harness against real puzzle blobs whose passwords are known.

Until the Phase 2 and Phase 3 ciphertexts turned up, every sweep had to try both
the MD5 KDF (OpenSSL 1.0) and the SHA-256 KDF (OpenSSL 1.1+) because there was
no way to tell which the creator used. These two blobs settle it.
"""
import base64, hashlib
from Crypto.Cipher import AES
from gsmg import Blob, evp_bytes_to_key

PHASE3_PARTS = [
    "causality", "Safenet", "Luna", "HSM", "11110",
    "0x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E6972"
    "62206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D6954"
    "20656854",
    "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1",
]

def main():
    ok = True

    # --- the seven-part password reproduces the documented digest exactly
    h = hashlib.sha256(''.join(PHASE3_PARTS).encode()).hexdigest()
    want = "1a57c572caf3cf722e41f5f9cf99ffacff06728a43032dd44c481c77d2ec30d5"
    print(f"phase 3 seven-part password: {'PASS' if h == want else 'FAIL'}  {h}")
    ok &= h == want

    # --- which KDF does the creator's own ciphertext use?
    b2 = Blob(''.join(open('source/phase2.txt').read().split()))
    pw2 = hashlib.sha256(b"causality").hexdigest()
    for md in ("sha256", "md5"):
        pt = b2.decrypt(pw2, md)
        got = pt is not None and pt.startswith(b"The ironic 2name of the keymakers")
        print(f"phase 2 with KDF {md:6s}: {'DECRYPTS' if got else 'fails'}")
        if md == "sha256":
            ok &= got
        else:
            ok &= not got
    print("\n=> the puzzle uses the SHA-256 KDF (OpenSSL 1.1+ defaults)")
    return ok

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
