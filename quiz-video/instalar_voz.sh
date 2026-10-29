#!/usr/bin/env bash
# Instala la voz Kokoro (gratuita, Apache-2.0) en este entorno. Solo usa PyPI y npm.
set -euo pipefail
cd "$(dirname "$0")"
pip install -q kokoro-onnx espeakng-loader
mkdir -p modelos && TMP=$(mktemp -d)
(cd "$TMP" && npm pack kokoro-q8-shards@1.0.0 kokoro-js@1.2.1 --silent >/dev/null \
  && mkdir kq kj && tar xzf kokoro-q8-shards-1.0.0.tgz -C kq && tar xzf kokoro-js-1.2.1.tgz -C kj)
cat "$TMP"/kq/package/kokoro-q8.part{0..5}.bin > modelos/kokoro-q8.onnx
echo "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478  modelos/kokoro-q8.onnx" | sha256sum -c -
python3 -I -c "
import numpy as np, glob, os, sys
d = {os.path.basename(f)[:-4]: np.fromfile(f, dtype=np.float32).reshape(-1, 1, 256)
     for f in glob.glob(sys.argv[1] + '/e*.bin')}
np.savez(sys.argv[2], **d); print('voces:', ', '.join(d))" "$TMP/kj/package/voices" modelos/voices-es.npz
rm -rf "$TMP"
