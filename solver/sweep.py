"""Sweep a candidate stream against a salted blob.

Two-stage filter:
  1. PKCS#7 padding on the final block  -> kills ~255/256 of wrong passwords for
     the cost of a single AES block decryption.
  2. Plaintext plausibility on the survivors -> the expected payload is a private
     key (64 hex chars, or a 51/52 char WIF) or English, i.e. printable ASCII.
     Random bytes essentially never pass, so a stage-2 survivor is a real hit.
"""
import hashlib, re, sys, time
import validate

# Plaintext commitments published as reproducibility anchors. Unverified -- they
# come from the same issue tracker that produced the fabricated #69 -- so they are
# an ADDITIONAL trigger, never a replacement for the existing filters. If they are
# wrong we lose nothing; if they are right they close a real hole, because until
# now a hit whose plaintext was binary rather than text would have been silently
# discarded by the printability filter.
ANCHORS = {
    "salphaseion-79B": "e2590f1581c75812c6848776f2979d3bf272a75cb95063f1b177a2bbf4992cbd",
    "cosmic-1327B":    "4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081",
}


def anchor_hit(pt):
    h = hashlib.sha256(pt).hexdigest()
    for name, want in ANCHORS.items():
        if h == want:
            return name
    return None
from gsmg import Blob, SALPHASEION_B64

BLOB = Blob(SALPHASEION_B64)
# Calibrated, not assumed: Phase 2 decrypts under sha256("causality") with the
# SHA-256 KDF and fails padding under MD5, and Phase 3 does the same under its
# seven-part password. The creator used OpenSSL 1.1+ defaults throughout, so
# every future sweep gets double the throughput by dropping MD5. (Past results
# stand -- both KDFs were tested, so SHA-256 was always covered.)
DIGESTS = ("sha256",)
PRINTABLE = set(range(0x20, 0x7f)) | {0x09, 0x0a, 0x0d}


KEYISH = re.compile(rb"[0-9a-fA-F]{64}|[5KL][1-9A-HJ-NP-Za-km-z]{50,51}")


def plausible(pt):
    """Deliberately looser than 'all printable': the payload might be a key
    embedded in binary, or text with one stray byte, and a filter that only
    accepts perfect ASCII would throw that away. Random bytes still essentially
    never reach 80% printable, so the noise floor stays at zero."""
    if pt is None or len(pt) < 8:
        return False
    if KEYISH.search(pt):
        return True
    return sum(b in PRINTABLE for b in pt) / len(pt) >= 0.80


def transforms(s):
    """The forms this puzzle has actually used a password in."""
    h1 = hashlib.sha256(s.encode()).hexdigest()
    yield "raw", s
    yield "sha256", h1
    yield "sha256^2", hashlib.sha256(h1.encode()).hexdigest()
    yield "sha256^2raw", hashlib.sha256(bytes.fromhex(h1)).hexdigest()


def run(stream, label, blob=BLOB, out=sys.stdout):
    t0, n, pad, hits = time.time(), 0, 0, []
    for base in stream:
        for tname, pw in transforms(base):
            for md in DIGESTS:
                n += 1
                pt = blob.check(pw, md)
                if pt is None:
                    continue
                pad += 1
                anc = anchor_hit(pt)
                if anc:
                    print(f"  *** ANCHOR {anc} base={base!r} form={tname} kdf={md}",
                          file=out, flush=True)
                if anc or plausible(pt):
                    hits.append((base, tname, md, pt))
                    print(f"  !!! HIT base={base!r} form={tname} kdf={md}\n"
                          f"      plaintext: {pt!r}", file=out, flush=True)
                    for key, addr in validate.check(pt):
                        print(f"      *** PRIZE ADDRESS {addr} <- {key}",
                              file=out, flush=True)
    dt = time.time() - t0
    print(f"[{label}] {n:,} decryptions in {dt:.1f}s ({n/max(dt,1e-9):,.0f}/s) | "
          f"{pad} passed padding (~{n/256:.0f} expected by chance) | "
          f"{len(hits)} plausible plaintexts", file=out, flush=True)
    return hits
