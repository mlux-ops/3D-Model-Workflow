# -*- coding: utf-8 -*-
"""Verified launcher for the complete F07 native Revit builder source."""
import os
import io
import gzip
import base64
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = [
    'build_nodes_payload.b64.0',
    'build_nodes_payload.b64.1',
    'build_nodes_payload.b64.2',
    'build_nodes_payload.b64.3a',
    'build_nodes_payload.b64.3b',
    'build_nodes_payload.b64.3c',
    'build_nodes_payload.b64.3d0',
    'build_nodes_payload.b64.3d1',
    'build_nodes_payload.b64.3d2',
    'build_nodes_payload.b64.3d3',
    'build_nodes_payload.b64.3d4',
    'build_nodes_payload.b64.3e0',
    'build_nodes_payload.b64.3e1',
    'build_nodes_payload.b64.3e2',
    'build_nodes_payload.b64.3e3',
    'build_nodes_payload.b64.3e4',
    'build_nodes_payload.b64.3f0',
    'build_nodes_payload.b64.3f1',
    'build_nodes_payload.b64.3f2',
    'build_nodes_payload.b64.3f3',
    'build_nodes_payload.b64.3f4',
    'build_nodes_payload.b64.4',
]
EXPECTED_SOURCE_SHA256 = 'c180adf547c050d366f6ced88164aba61ca895ce6a8a922484edf67456bda8c9'
EXPECTED_SOURCE_BYTES = 29726

encoded = ''
for name in PARTS:
    path = os.path.join(HERE, name)
    if not os.path.isfile(path):
        raise RuntimeError('Missing verified builder payload segment: ' + path)
    with open(path, 'r') as stream:
        encoded += stream.read().strip()
compressed = base64.b64decode(encoded)
with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode='rb') as stream:
    payload = stream.read()
actual = hashlib.sha256(payload).hexdigest()
if len(payload) != EXPECTED_SOURCE_BYTES or actual != EXPECTED_SOURCE_SHA256:
    raise RuntimeError('Native builder payload integrity failure: bytes=%s sha256=%s' % (len(payload), actual))
expanded = os.path.join(HERE, 'build_nodes_payload_expanded.py')
with open(expanded, 'wb') as stream:
    stream.write(payload)
source = payload.decode('utf-8')
exec(compile(source, expanded, 'exec'), globals(), globals())
