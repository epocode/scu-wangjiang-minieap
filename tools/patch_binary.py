"""GPL-3.0: reproduce the 2026-10-11 patch for one exact ARM64 build."""
import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA256 = 'a905f0db341e76557ae92f706fcfc5c1fdb1fa3201c971bf1342d9941101eafb'
PATCHED_SHA256 = '459fe82e2d2aa2747967bcd13e048faabce327d018817361eb9505501bf1dc16'
CHANGES = (
    (0x31A4, bytes.fromhex('20e08352'), bytes.fromhex('c0408a52')),
    (0x31AC, bytes.fromhex('2040a072'), bytes.fromhex('0000a072')),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.original.resolve() == args.output.resolve():
        parser.error('Input and output must be different; keep the original for rollback.')
    if args.output.exists():
        parser.error('Output already exists; choose a new path.')
    original = args.original.read_bytes()
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        parser.error('Original SHA256 differs from the tested build. No patch applied.')
    patched = bytearray(original)
    for offset, old, new in CHANGES:
        if patched[offset:offset + len(old)] != old:
            parser.error('Unexpected instruction. No patch applied.')
        patched[offset:offset + len(old)] = new
    if hashlib.sha256(patched).hexdigest() != PATCHED_SHA256:
        parser.error('Unexpected patched SHA256. No output written.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(patched)
    print(f'Created {args.output}\nSHA256: {PATCHED_SHA256}')


if __name__ == '__main__':
    main()
