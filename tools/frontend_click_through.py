import requests
import json
BASE = 'http://127.0.0.1:8000'
headers = {'X-Merchant-Id': 'MERCH_TEST'}

# Choose which menu to fetch; set to 'retention' to exercise retention executor menu
MENU_TARGET = 'retention'  # change to 'merchant' for merchant menus

if MENU_TARGET == 'retention':
    # retention executor menu is provided under the 'icp_hr' company_type
    menu_url = '/api/menu/icp_hr?role=retention_executor'
else:
    menu_url = '/api/menu/merchant?role=merchant_manager'

# Fetch menu
r = requests.get(BASE + menu_url, timeout=5)
print('menu', r.status_code)
menu_json = r.json()
# normalize response: endpoint may return {status, data: [...]}
if isinstance(menu_json, dict) and 'data' in menu_json:
    menu_data = menu_json.get('data')
else:
    menu_data = menu_json

endpoints = []
if isinstance(menu_data, list):
    for m in menu_data:
        # m may sometimes be a string or malformed; guard accordingly
        if isinstance(m, dict):
            for s in m.get('submenus', []):
                if isinstance(s, dict) and s.get('api_endpoint'):
                    endpoints.append(s.get('api_endpoint'))
        else:
            # skip unexpected entries
            continue
else:
    print('Unexpected menu data shape:', type(menu_data))

print('found endpoints:', endpoints)

# define which endpoints to POST sample payloads for
post_examples = {
    '/api/merchant/staff/add-employee': {'name': 'Auto Test', 'role': 'Cashier'},
    '/api/merchant/staff/salary': {'employee_id': 'EMP001', 'amount': 1000},
    '/api/merchant/marketing/create-campaign': {'campaign_name': 'AutoCamp', 'budget': 100},
    '/api/merchant/notifications/settings': {'email': False, 'sms': True, 'in_app': True},
    '/api/merchant/feedback-ideas': {'content': 'Auto feedback from test'},
}

results = {}
for e in endpoints:
    try:
        if e in post_examples:
            rr = requests.post(
                BASE + e, json=post_examples[e], headers=headers, timeout=5)
        else:
            rr = requests.get(BASE + e, headers=headers, timeout=5)
        try:
            data = rr.json()
        except Exception:
            data = rr.text
        results[e] = {'status': rr.status_code, 'data': data}
        print(e, rr.status_code, (data if isinstance(
            data, dict) else str(data)[:200]))
    except Exception as exc:
        results[e] = {'status': 'ERR', 'error': str(exc)}
        print('ERR', e, exc)

# write results to file
with open('tools/frontend_click_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\nSaved results to tools/frontend_click_results.json')
