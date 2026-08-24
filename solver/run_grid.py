import hashlib, sys
import validate
from grid import all_candidates
from sweep import plausible
from pagehash import BLOBS

seen, n, hits = set(), 0, 0
for tag, base in all_candidates():
    if base in seen:
        continue
    seen.add(base)
    h1 = hashlib.sha256(base.encode()).hexdigest()
    forms = (("raw", base), ("sha256", h1),
             ("sha256^2", hashlib.sha256(h1.encode()).hexdigest()),
             ("sha256^2raw", hashlib.sha256(bytes.fromhex(h1)).hexdigest()))
    for fname, pw in forms:
        for md in ("md5", "sha256"):
            for bname, blob in BLOBS.items():
                n += 1
                pt = blob.check(pw, md)
                if pt is not None and plausible(pt):
                    hits += 1
                    print(f"!!! HIT blob={bname} tag={tag} form={fname} kdf={md}\n"
                          f"    base={base[:80]}\n    {pt[:200]!r}", flush=True)
                    for key, addr in validate.check(pt):
                        print(f"    *** PRIZE ADDRESS {addr} <- {key}", flush=True)
print(f"[grid] {len(seen):,} distinct base strings, {n:,} decryptions, "
      f"{hits} plausible plaintexts")
