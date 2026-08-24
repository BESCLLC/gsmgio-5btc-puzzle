"""Does A or C decode to the PRIZE PRIVATE KEY itself?

All four blobs are open, so no A/C-derived key can be validated against them --
their keys are known and none is an A/C decode. If A or C decodes to anything,
it is not a blob key. The creator says everything needed is on the page and that
what you are looking for is the private key. So test that literally: every digit
assignment, every 32-byte window of the decoded payload, against the prize
HASH160.

This is the one test that needs no locked door.
"""
import hashlib, itertools, sys, time
from coincurve import PrivateKey
import validate

LETTERS = "abcdefghi"
N = validate.N
TARGETS = set()
for addr in validate.PRIZE:
    n = 0
    for ch in addr:
        n = n * 58 + validate.B58.index(ch)
    TARGETS.add(n.to_bytes(25, "big")[1:21])


def h160(pub):
    return hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()


def decode(s, m):
    n = 0
    for c in s:
        n = n * 10 + m[c]
    h = f"{n:x}"
    if len(h) % 2:
        h = "0" + h
    try:
        return bytes.fromhex(h)
    except ValueError:
        return b""


def hunt(name, s, elite=None):
    src = s if elite is None else elite
    t0 = time.time(); n = 0
    for digits in ("123456789", "012345678"):
        for perm in itertools.permutations(digits):
            m = dict(zip(LETTERS, [int(d) for d in perm]))
            bs = decode(src, m)
            for off in range(0, max(0, len(bs) - 31)):
                w = bs[off:off + 32]
                v = int.from_bytes(w, "big")
                if not (0 < v < N):
                    continue
                n += 1
                pk = PrivateKey(w).public_key
                for comp in (True, False):
                    if h160(pk.format(comp)) in TARGETS:
                        print(f"\n*** PRIZE KEY FOUND ***")
                        print(f"    source={name} map={''.join(perm)} offset={off}")
                        print(f"    privkey={w.hex()}")
                        print(f"    compressed={comp}")
                        sys.exit(0)
            if n and n % 500000 < 250:
                print(f"  {name}: {n:,} keys, {time.time()-t0:.0f}s",
                      file=sys.stderr, flush=True)
    print(f"[{name}] {n:,} candidate keys tested in {time.time()-t0:.0f}s -- no prize")


ALPH = LETTERS
def elite9(raw, d):
    v = [ALPH.index(c) for c in raw]
    hi = [x // 3 for x in v]; lo = [x % 3 for x in v]
    lo = lo[-1:] + lo[:-1] if d == "right" else lo[1:] + lo[:1]
    return "".join(ALPH[3*h + l] for h, l in zip(hi, lo))


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "A"
    raw = open(f"part{which}.txt").read().strip()
    hunt(f"part{which}", raw)
    for d in ("right", "left"):
        hunt(f"part{which}/ELITE-{d}", raw, elite9(raw, d))
