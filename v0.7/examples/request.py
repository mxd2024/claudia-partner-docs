"""Send one reviewed JSON request. Credentials stay out of files and output."""
import argparse,getpass,json,os,ssl,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlsplit
p=argparse.ArgumentParser(description=__doc__);p.add_argument("--base",required=True);p.add_argument("--request",required=True,type=Path);p.add_argument("--ca")
a=p.parse_args();u=urlsplit(a.base)
assert u.scheme=="https" and u.netloc and not u.username and not u.password and not u.query and not u.fragment and u.path in ("","/"),"Use a Core HTTPS origin"
s=json.loads(a.request.read_text(encoding="utf-8"));assert s["url"].startswith("/") and not s["url"].startswith("//") and not urlsplit(s["url"]).netloc
h={k:v for k,v in s.get("headers",{}).items() if k.lower() not in ("authorization","host","cookie")}
token=os.environ.get("CP_ACCESS_TOKEN") or getpass.getpass("Access token: ");h["Authorization"]="Bearer "+token
body=json.dumps(s["body"],ensure_ascii=False).encode() if "body" in s else None
if body is not None:h.setdefault("Content-Type","application/json")
req=urllib.request.Request(a.base.rstrip("/")+s["url"],data=body,headers=h,method=s["method"])
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
opener=urllib.request.build_opener(NoRedirect(),urllib.request.HTTPSHandler(context=ssl.create_default_context(cafile=a.ca)))
try:
 with opener.open(req,timeout=30) as res:print(res.status);print(res.read().decode("utf-8"))
except urllib.error.HTTPError as ex:
 print(ex.code);print(ex.read().decode("utf-8"));raise SystemExit(1)
