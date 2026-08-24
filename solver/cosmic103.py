"""The 103x103 construction, ready to run the moment a verified Cosmic
plaintext exists.

Usage: python3 cosmic103.py <path-to-cosmic.dec>

This session has never decrypted the Cosmic Duality blob, so there is nothing to
feed it yet. It is written to be decisive when there is: it checks the input's
own SHA-256 against the claimed one, runs the construction, and compares against
the three published checkpoints instead of just printing numbers.
"""
import hashlib, sys

CLAIMED_SHA = "4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081"
CHECKPOINTS = {
    "HALF":   "0423d9115a1dc756d5d08d2de880ab508bd4745fc97709f4fcb513f2cb8fcc35",
    "BETTER": "48cc46e66bdd36b09ae344552f606a761f9d90681f20dfefe2b43db18b623971",
    "TRAIL":  "fc0c1b02",
}
N = 103


def construct(data):
    bits = "".join(f"{x:08b}" for x in data)
    mbits, remainder = bits[:N * N], bits[N * N:]
    M = [[int(x) for x in mbits[r * N:(r + 1) * N]] for r in range(N)]
    rows = [sum(r) for r in M]
    cols = [sum(M[r][c] for r in range(N)) for c in range(N)]
    secondary = [rows[i] + cols[(i + 7) % N] for i in range(N)]
    return secondary, remainder


def main(path):
    data = open(path, "rb").read()
    got = hashlib.sha256(data).hexdigest()
    print(f"input: {len(data)} bytes, sha256 {got}")
    print(f"  length 1327: {len(data) == 1327}")
    print(f"  sha256 matches claim: {got == CLAIMED_SHA}")
    if len(data) != 1327:
        print("  -> construction assumes 1327 bytes; aborting")
        return 1

    secondary, remainder = construct(data)
    lo, hi = min(secondary), max(secondary)
    print(f"\nsecondary: {len(secondary)} values, range {lo}-{hi} (span {hi-lo+1})")
    print(f"  remainder bits: {remainder}")
    print(f"  all within [80,117]: {lo >= 80 and hi <= 117}")
    if not (lo >= 80 and hi <= 117):
        print("  -> outside the base-38 window the construction assumes")
        return 1
    print(f"  as ASCII: {bytes(secondary).decode('ascii')}")

    n = 0
    for d in (x - 80 for x in secondary):
        n = n * 38 + d
    out = n.to_bytes(68, "big")
    parts = {"HALF": out[:32].hex(), "BETTER": out[32:64].hex(), "TRAIL": out[64:].hex()}
    print()
    allok = True
    for k, v in parts.items():
        ok = v == CHECKPOINTS[k]
        allok &= ok
        print(f"  {k:7s} {v}  {'MATCH' if ok else 'MISMATCH (expected ' + CHECKPOINTS[k] + ')'}")

    if allok:
        import validate
        print("\nall three checkpoints hit. Testing the scalars against the prize:")
        for k in ("HALF", "BETTER"):
            for a in validate.addresses(int(parts[k], 16)):
                mark = " *** PRIZE ***" if a in validate.PRIZE else ""
                print(f"  {k}: {a}{mark}")
    return 0 if allok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        print("No Cosmic plaintext exists in this session -- nothing to run against.")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
