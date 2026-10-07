"""Package exactly the verified public manifest; omit Git, sources and local QA."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
subprocess.run([sys.executable,str(ROOT/'tools/verify_site.py')],check=True,cwd=ROOT)
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
args.output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
    for name in sorted(set(manifest['files'])|{'manifest.json'}):
        path=ROOT/name
        assert path.is_file() and not path.is_symlink()
        assert path.resolve().is_relative_to(ROOT)
        info=zipfile.ZipInfo(name,date_time=(2026,10,7,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,path.read_bytes())
print(json.dumps({'archive':str(args.output),'files':len(manifest['files'])+1,'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),'target_url':manifest['public_base_url']},ensure_ascii=False,indent=2))
