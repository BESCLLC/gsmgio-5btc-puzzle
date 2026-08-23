"""'Our first hint is your last command.'

The first hint of the whole puzzle was HASHTHETEXT, and it worked like this:
take the text as displayed on the page, strip spaces and punctuation, keep the
case, SHA-256 it. That is literally how you reach SalPhaseIon:

    sha256("GSMGIO5BTCPUZZLECHALLENGE" + "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe")
      = 89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32

If the SalPhaseIon page means that instruction as literally as the first page
did, the password is a hash of this page's own text -- and "shabef ans too"
says to hash the answer a second time. That needs the exact page source, which
is why this could not be tested from a transcription.
"""
import base64, hashlib, itertools
from gsmg import Blob

SALP_SPACED = open('source/salphaseion_raw.txt').read().strip('\n')
COSMIC_RAW = open('source/cosmic_duality.txt').read()

SALP_FLAT = ''.join(SALP_SPACED.split())
COSMIC_FLAT = ''.join(COSMIC_RAW.split())

# the SalPhaseIon blob, rebuilt from the page (the "enter" bits sit between the
# two base64 runs and are not part of it)
i = SALP_FLAT.index('U2FsdGVkX18')
tail = SALP_FLAT[i:]
SMALL_B64 = tail[:64] + tail[64 + 40:64 + 40 + 64]

TITLES = ("SalPhaseIon", "CosmicDuality", "SalPhaseIonCosmicDuality")

def texts():
    """Every reasonable reading of 'the text' on this page."""
    yield "stream-flat", SALP_FLAT
    yield "stream-spaced", SALP_SPACED
    yield "cosmic-flat", COSMIC_FLAT
    yield "cosmic-raw", COSMIC_RAW
    yield "both-flat", SALP_FLAT + COSMIC_FLAT
    yield "both-spaced", SALP_SPACED + "\n" + COSMIC_RAW
    for t in TITLES:
        yield f"{t}+stream", t + SALP_FLAT
        yield f"{t}+both", t + SALP_FLAT + COSMIC_FLAT
    yield "titled", "SalPhaseIon" + SALP_FLAT + "CosmicDuality" + COSMIC_FLAT
    # symbols only, i.e. the block with the embedded base64 removed
    yield "symbols-only", SALP_FLAT[:SALP_FLAT.index('U2FsdGVkX18')]
    yield "SalPhaseIon+symbols", "SalPhaseIon" + SALP_FLAT[:SALP_FLAT.index('U2FsdGVkX18')]


def variants(s):
    yield "as-is", s
    yield "upper", s.upper()
    yield "lower", s.lower()
    yield "alnum", ''.join(c for c in s if c.isalnum())
    yield "alnum-upper", ''.join(c for c in s if c.isalnum()).upper()


def passwords(s):
    h1 = hashlib.sha256(s.encode()).hexdigest()
    yield "sha256", h1
    yield "sha256^2", hashlib.sha256(h1.encode()).hexdigest()          # "ans too"
    yield "sha256^2raw", hashlib.sha256(bytes.fromhex(h1)).hexdigest()
    yield "raw", s if len(s) < 200 else h1


BLOBS = {"salphaseion": Blob(SMALL_B64), "cosmic": Blob(COSMIC_FLAT)}

if __name__ == "__main__":
    import validate
    from sweep import plausible
    n = hits = 0
    for tname, text in texts():
        for vname, v in variants(text):
            for pname, pw in passwords(v):
                for md in ("md5", "sha256"):
                    for bname, blob in BLOBS.items():
                        n += 1
                        pt = blob.check(pw, md)
                        if pt is not None and plausible(pt):
                            hits += 1
                            print(f"!!! HIT blob={bname} text={tname} form={vname} "
                                  f"pw={pname} kdf={md}\n    {pt[:200]!r}")
                            for key, addr in validate.check(pt):
                                print(f"    *** PRIZE ADDRESS {addr} <- {key}")
    print(f"[page-text hashes] {n:,} decryptions, {hits} plausible plaintexts")
    print(f"  small blob rebuilt from page source matches README assembly: "
          f"{SMALL_B64 == open('gsmg.py').read().count('U2FsdGVkX186') > 0}")
