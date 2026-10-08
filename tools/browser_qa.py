import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'.qa'
QA.mkdir(exist_ok=True)
config=json.loads((ROOT/'site-source/site.json').read_bytes())
report={'browser':'isolated headless Chromium on the user PC','viewports':[],'checks':[],'errors':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.on('console',lambda msg:report['errors'].append(msg.text) if msg.type=='error' else None)
    for width in [1440,390,320]:
        page.set_viewport_size({'width':width,'height':1000})
        for path in ['index.html','v0.7/guides.html','v0.7/quickstart.html','v0.7/api.html','v0.7/api-media.html','v0.7/releases.html','v0.7/sample-app.html','v0.7/request-access.html','v0.7/versions.html','v0.7/mcp.html','v0.7/media.html','v0.7/api-service-access.html','v0.7/app-architecture.html','v0.7/authentication.html']:
            r=page.goto('http://127.0.0.1:8765/'+path)
            assert r.status==200
            assert page.locator('h1').count()==1
            overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
            assert not overflow,(width,path,'horizontal overflow')
            report['viewports'].append({'width':width,'page':path,'horizontal_overflow':False})
        page.goto('http://127.0.0.1:8765/')
        page.screenshot(path=str(QA/f'home-{width}.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto('http://127.0.0.1:8765/')
    search=page.locator('#site-search')
    for query in ['BFF','OIDC','404','画像','Idempotency-Key','query','ＭＣＰ','service.metadata','service.import','ケース','接続相談','1.0.1','Mac','VPS','併存','戻り先','Cookie']:
        search.fill(query)
        page.wait_for_function('document.querySelectorAll("#search-results a").length > 0')
        assert page.locator('#search-results').is_visible()
        report['checks'].append({'search':query,'results':page.locator('#search-results a').count()})
        search.press('Escape')
        assert not page.locator('#search-results').is_visible()
    search.fill('絶対に一致しない検査語')
    page.wait_for_function('document.querySelector("#search-results").textContent.includes("一致するページはありません")')
    report['checks'].append({'search_no_results':True})
    search.fill('BFF')
    page.wait_for_function('document.querySelectorAll("#search-results a").length > 0')
    search.press('ArrowDown')
    assert page.locator('#search-results a').first.evaluate('(e)=>document.activeElement===e')
    page.keyboard.press('Enter')
    page.wait_for_url('**/v0.7/*.html')
    report['checks'].append({'keyboard_search_navigation':True})
    page.goto('http://127.0.0.1:8765/v0.7/api.html')
    page.locator('#api-search').fill('media')
    visible=page.locator('.operation-row:visible').count()
    assert visible==16
    page.locator('#api-group').select_option('media')
    page.locator('#api-search').fill('不一致')
    assert page.locator('#empty-result').is_visible()
    page.locator('#clear-search').click()
    assert page.locator('.operation-row:visible').count()==config['expected_operations']
    report['checks'].append({'api_filter_and_clear':True,'media_operations':visible})
    page.goto('http://127.0.0.1:8765/v0.7/api.html#op-health-live')
    page.wait_for_url('**/api-health.html#op-health-live')
    assert page.locator('#op-health-live').get_attribute('open') is not None
    report['checks'].append({'legacy_operation_deep_link':True})
    for operation in ['service-metadata','service-import']:
        page.goto('http://127.0.0.1:8765/v0.7/api.html#op-'+operation)
        page.wait_for_url('**/api-service-access.html#op-'+operation)
        assert page.locator('#op-'+operation).get_attribute('open') is not None
        report['checks'].append({'new_operation_deep_link':operation})
    page.goto('http://127.0.0.1:8765/v0.7/api.html#schema-Problem')
    page.wait_for_url('**/api-schemas.html#schema-Problem')
    assert page.locator('#schema-Problem').get_attribute('open') is not None
    report['checks'].append({'legacy_schema_deep_link':True})
    page.goto('http://127.0.0.1:8765/v0.7/app-architecture.html')
    body=page.locator('main').inner_text()
    for text in ['Macで開発し、VPSへ移す設計','併存登録','準備中','設定の差分','Cookie','SSH転送','独自の認証局','正本・実機受入の確認待ち']:
        assert text in body,text
    report['checks'].append({'migration_requirements_and_preparing_state_rendered':True})
    page.set_viewport_size({'width':320,'height':700})
    page.goto('http://127.0.0.1:8765/v0.7/quickstart.html')
    page.locator('.menu-toggle').click()
    assert page.locator('#navigation').is_visible()
    assert page.locator('.menu-toggle').get_attribute('aria-expanded')=='true'
    assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
    page.locator('#site-search').fill('404')
    page.wait_for_function('document.querySelectorAll("#search-results a").length > 0')
    report['checks'].append({'mobile_menu_and_search':True})
    page.screenshot(path=str(QA/'mobile-menu.png'),full_page=True)
    browser.close()
report['passed']=not report['errors']
(QA/'browser-report.json').write_bytes(json.dumps(report,ensure_ascii=False,indent=2).encode('utf-8'))
print(json.dumps(report,ensure_ascii=False,indent=2))
assert report['passed']
