import requests
import json
BASE = 'http://127.0.0.1:8000'
headers = {'X-Merchant-Id': 'MERCH_TEST'}
endpoints = [
    '/api/retention/assigned-merchants',
    '/api/icp/executor/assigned-merchants',
    '/api/retention/merchant-profile?merchant_id=MERCH1001',
    '/api/retention/merchant-profile',
    '/api/icp/executor/merchant-profile/MERCH1001',
    '/api/retention/mark-activity-complete',
    '/api/retention/submit-summary-report',
    '/api/retention/update-merchant-health',
    '/api/retention/log-merchant-needs',
    '/api/retention/add-notes-commitments',
    '/api/retention/attach-photo-proof',
    '/api/chatbot/daily_followups'
]
results = {}
for e in endpoints:
    try:
        url = BASE + e
        # if endpoint expects POST, some are POST; try GET first, fallback to POST
        rr = requests.get(url, headers=headers, timeout=5)
        if rr.status_code == 405:  # method not allowed, try POST
            rr = requests.post(url, json={}, headers=headers, timeout=5)
        try:
            data = rr.json()
        except Exception:
            data = rr.text
        results[e] = {'status': rr.status_code, 'data': data}
        print(e, rr.status_code)
    except Exception as exc:
        results[e] = {'status': 'ERR', 'error': str(exc)}
        print('ERR', e, exc)
with open('tools/check_retention_direct_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('Saved tools/check_retention_direct_results.json')
