"""Create a local environment-specific OpenAPI copy; never handles credentials."""
import argparse, json
from pathlib import Path
from urllib.parse import urlsplit
p=argparse.ArgumentParser(description=__doc__)
for name in ("source","profile","output"): p.add_argument("--"+name,required=True,type=Path)
a=p.parse_args();s=json.loads(a.source.read_text());c=json.loads(a.profile.read_text())
for key in ("core_origin","issuer","token_endpoint"):
 u=urlsplit(c[key]);assert u.scheme=="https" and u.netloc and not u.username and not u.password and not u.query and not u.fragment,key
assert urlsplit(c["core_origin"]).path in ("","/"),"Core must be an origin"
s["servers"]=[{"url":c["core_origin"].rstrip("/")}]
s["components"]["securitySchemes"]["humanOidc"]["openIdConnectUrl"]=c["issuer"].rstrip("/")+"/.well-known/openid-configuration"
s["components"]["securitySchemes"]["serviceOAuth"]["flows"]["clientCredentials"]["tokenUrl"]=c["token_endpoint"]
with a.output.open("x",encoding="utf-8") as f: json.dump(s,f,ensure_ascii=False,indent=2)
print("Created environment OpenAPI; client registration and PKCE support remain required.")
