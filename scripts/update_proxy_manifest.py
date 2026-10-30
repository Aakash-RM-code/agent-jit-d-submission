"""Refresh release hashes for the Render/Vercel connection patch."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
target = root / 'RELEASE_MANIFEST.json'
manifest = json.loads(target.read_text())
for name in ('jitd/server.py', 'jitd/boundary.py', 'jitd/origins.py',
             'tests/test_public_origin.py', 'vercel-frontend/vercel.json',
             'vercel-frontend/public/proxy-info.txt', 'scripts/update_proxy_manifest.py'):
    manifest['files'][name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
target.write_text(json.dumps(manifest, indent=2) + '\n')
print('Release manifest updated for Vercel connection patch.')
