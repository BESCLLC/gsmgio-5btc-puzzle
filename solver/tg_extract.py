#!/usr/bin/env python3
"""Extract COMPLETE Salted__ blobs from a Telegram HTML export.

The naive grep for U2FsdGVk returns one 64-character line, because that is how
OpenSSL wraps base64. Every blob in the dump therefore looks like 32 bytes of
ciphertext no matter its true size -- Phase 2 (656B), Cosmic (1328B) and
Phase 3.2 (2432B) all present identically. Continuation lines must be joined.

Usage:  python3 tg_extract.py /path/to/messages*.html
"""
import base64, html, re, sys
from collections import defaultdict

B64 = r"[A-Za-z0-9+/=]"
# a blob is a starting line, then any number of continuation lines. Telegram
# separates them with <br>, </div><div>, newlines, or nothing at all.
SEP = r"(?:\s|<br\s*/?>|</?div[^>]*>|</?p[^>]*>|&nbsp;)*"
PAT = re.compile(rf"(U2FsdGVk{B64}{{8,}}(?:{SEP}{B64}{{16,}})*)", re.I)


def blobs_in(text):
    text = html.unescape(text)
    for m in PAT.finditer(text):
        run = re.sub(rf"(?:{SEP})", "", m.group(1))
        run = re.sub(r"[^A-Za-z0-9+/=]", "", run)
        # take the longest prefix that is a valid, block-aligned salted object
        for L in range(len(run) - (len(run) % 4), 16, -4):
            try:
                raw = base64.b64decode(run[:L])
            except Exception:
                continue
            if raw[:8] == b"Salted__" and len(raw) >= 32 and (len(raw) - 16) % 16 == 0:
                yield raw[8:16].hex(), len(raw) - 16, run[:L]
                break


def main(paths):
    best = {}
    for p in paths:
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print(f"  skip {p}: {e}", file=sys.stderr); continue
        for salt, ctlen, b64 in blobs_in(t):
            # keep the LONGEST capture seen for each salt
            if salt not in best or ctlen > best[salt][0]:
                best[salt] = (ctlen, b64, p)
    print(f"{len(best)} distinct salts\n")
    for salt, (ctlen, b64, p) in sorted(best.items(), key=lambda kv: -kv[1][0]):
        blocks = ctlen // 16
        note = "  <-- 5 blocks: could hold a 79-byte record" if blocks == 5 else ""
        print(f"salt={salt}  ct={ctlen}B ({blocks} blk)  from {p}{note}")
        print(f"  {b64}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    main(sys.argv[1:])
