from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
pages=[n for n in manifest['files'] if n.endswith('.html')]
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':320,'height':800})
    for name in pages:
        response=page.goto('http://127.0.0.1:8765/'+name)
        assert response.status==200
        details=page.locator('main details')
        if details.count(): details.first.locator('summary').click()
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),name
        results.append({'page':name,'width':320,'no_horizontal_overflow':True,'detail_opened':details.count()>0})
    browser.close()
(root/'.qa/all-pages-report.json').write_bytes(json.dumps({'passed':True,'pages':results},ensure_ascii=False,indent=2).encode('utf-8'))
print('All',len(results),'pages pass at 320px, with the first operation/schema expanded where present.')
