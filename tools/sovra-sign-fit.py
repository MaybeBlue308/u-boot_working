#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0+
"""Sign an ITS and add its required configuration key to a control DTB copy."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('its', 'control-dtb', 'key-dir', 'mkimage', 'fit-check-sign',
                 'out-fit', 'out-dtb'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--key-name', required=True)
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.key_name):
        parser.error('key name must contain only letters, digits, _ or -')
    if not re.fullmatch(r'[A-Za-z0-9_.+-]+', args.config):
        parser.error('invalid configuration name')
    its, dtb, keydir = (p.resolve(strict=True) for p in
                        (args.its, args.control_dtb, args.key_dir))
    mkimage, checker = (p.resolve(strict=True) for p in
                        (args.mkimage, args.fit_check_sign))
    for suffix in ('.key', '.crt'):
        if not (keydir / (args.key_name + suffix)).is_file():
            parser.error('missing key/certificate: ' + args.key_name + suffix)
    out_fit, out_dtb = args.out_fit.resolve(), args.out_dtb.resolve()
    if out_fit == out_dtb or out_fit in (its, dtb) or out_dtb in (its, dtb):
        parser.error('output paths must be distinct from each other and inputs')
    if out_fit.exists() or out_dtb.exists():
        parser.error('output already exists; select new output paths')
    for out in (out_fit, out_dtb):
        if not out.parent.is_dir():
            parser.error('output parent directory does not exist: ' + str(out.parent))
    # Padding is required for mkimage to add the public key to the DTB.
    with tempfile.TemporaryDirectory(prefix='sovra-fit-') as tmp:
        temp = Path(tmp)
        temp_dtb, temp_fit = temp / 'control.dtb', temp / 'signed.itb'
        subprocess.run(['dtc', '-I', 'dtb', '-O', 'dtb', '-p', '4096',
                        '-o', str(temp_dtb), str(dtb)], check=True)
        subprocess.run([str(mkimage), '-f', str(its), '-k', str(keydir),
                        '-K', str(temp_dtb), '-r', str(temp_fit)],
                       cwd=its.parent, check=True)
        key_node = '/signature/key-' + args.key_name
        for prop, expected in (('required', 'conf'), ('algo', 'sha256,rsa2048')):
            result = subprocess.run(['fdtget', '-t', 's', str(temp_dtb),
                                     key_node, prop], check=True,
                                    text=True, capture_output=True).stdout.strip()
            if result != expected:
                raise ValueError(f'{key_node} {prop}: expected {expected}, got {result}')
        subprocess.run([str(checker), '-f', str(temp_fit), '-k', str(temp_dtb),
                        '-c', args.config], check=True)
        # Only publish verified outputs; inputs and existing files stay intact.
        for src, dst in ((temp_fit, out_fit), (temp_dtb, out_dtb)):
            with src.open('rb') as source, dst.open('xb') as target:
                shutil.copyfileobj(source, target)
    print('FIT:', out_fit)
    print('control DTB:', out_dtb)
    print('Host signature check passed; board policy and chain of trust remain unverified.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'sovra-sign-fit: {exc}', file=sys.stderr)
        sys.exit(1)
