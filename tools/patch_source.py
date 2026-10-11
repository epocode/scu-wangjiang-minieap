"""GPL-3.0: change the fixed rjv3 version array; review before compiling."""
import argparse
from pathlib import Path
import re

PATTERN = re.compile(
    rb'(uint8_t\s+_version\s*\[\s*4\s*\]\s*=\s*)'
    rb'\{\s*0x01\s*,\s*0x1[fF]\s*,\s*0x01\s*,\s*0x02\s*\}'
)
NEW_ARRAY = b'{0x06, 0x52, 0x00, 0x00}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root', type=Path)
    args = parser.parse_args()
    path = args.source_root / 'packet_plugin/rjv3/packet_plugin_rjv3_priv.c'
    data = path.read_bytes()
    start = data.find(b'static void rjv3_append_priv_header(')
    end = data.find(b'\n}', start)
    if start < 0 or end < 0:
        parser.error('Expected function boundaries not found. No file changed.')
    function = data[start:end]
    if len(PATTERN.findall(function)) != 1:
        parser.error('Expected exactly one original version array. No file changed.')
    function = PATTERN.sub(lambda match: match[1] + NEW_ARRAY, function)
    updated = data[:start] + function + data[end:]
    path.write_bytes(updated)
    print(f'Modified {path}; inspect git diff and build for your target architecture.')


if __name__ == '__main__':
    main()
