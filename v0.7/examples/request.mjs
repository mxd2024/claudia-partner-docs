// Send one reviewed JSON request. Node.js >=22; no automatic retries.
import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const args=process.argv.slice(2),arg=n=>args[args.indexOf(n)+1];
assert(args.includes('--base')&&args.includes('--request'),'--base and --request required');
const base=new URL(arg('--base'));
assert(base.protocol==='https:'&&base.pathname==='/'&&!base.username&&!base.password&&!base.search&&!base.hash,'Core HTTPS origin required');
const s=JSON.parse(await readFile(arg('--request'),'utf8'));
const url=new URL(s.url,base);assert(url.origin===base.origin&&s.url.startsWith('/')&&!s.url.startsWith('//'));
assert(process.env.CP_ACCESS_TOKEN,'CP_ACCESS_TOKEN required');
const headers=Object.fromEntries(Object.entries(s.headers??{}).filter(([k])=>!['authorization','host','cookie'].includes(k.toLowerCase())));
headers.Authorization='Bearer '+process.env.CP_ACCESS_TOKEN;
if(s.body!==undefined)headers['Content-Type']??='application/json';
const response=await fetch(url,{method:s.method,headers,body:s.body===undefined?undefined:JSON.stringify(s.body),redirect:'error',signal:AbortSignal.timeout(30000)});
console.log(response.status);console.log(await response.text());if(!response.ok)process.exitCode=1;
