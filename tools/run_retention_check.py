import requests, json
BASE='http://127.0.0.1:8000'
headers={'X-Merchant-Id':'MERCH_TEST'}
r = requests.get(BASE + '/api/menu/icp_hr?role=retention_executor', timeout=5)
print('menu', r.status_code)
menu_json = r.json()
if isinstance(menu_json, dict) and 'data' in menu_json:
    menu_data = menu_json.get('data')
else:
    menu_data = menu_json
endpoints = []
if isinstance(menu_data, list):
    for m in menu_data:
        if isinstance(m, dict):
            for s in m.get('submenus', []):
                if isinstance(s, dict) and s.get('api_endpoint'):
                    endpoints.append(s.get('api_endpoint'))
print('found endpoints:', endpoints)
results = {}
for e in endpoints:
    try:
        rr = requests.get(BASE + e, headers=headers, timeout=5)
        try:
            data = rr.json()
        except Exception:
            data = rr.text
        results[e] = {'status': rr.status_code, 'data': data}
        print(e, rr.status_code)
    except Exception as exc:
        results[e] = {'status': 'ERR', 'error': str(exc)}
        print('ERR', e, exc)
with open('tools/frontend_retention_results.json','w',encoding='utf-8') as f:
    json.dump(results,f,ensure_ascii=False,indent=2)
print('Saved retention results')
