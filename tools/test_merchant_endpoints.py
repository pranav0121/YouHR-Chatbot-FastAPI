import requests
import json
base = 'http://127.0.0.1:8000'
paths = ['/api/merchant/sales/today', '/api/merchant/sales/weekly',
         '/api/merchant/expenses/bills', '/api/merchant/staff/attendance']
for p in paths:
    try:
        r = requests.get(base+p, headers={'X-Merchant-Id': '1'}, timeout=5)
        print(p, r.status_code, r.json())
    except Exception as e:
        print('ERR', p, e)
# POST add employee
try:
    r = requests.post(base+'/api/merchant/staff/add-employee', json={
                      'name': 'Test User', 'role': 'Cashier'}, headers={'X-Merchant-Id': '1'}, timeout=5)
    print('/add-employee', r.status_code, r.json())
except Exception as e:
    print('ERR add-employee', e)
# POST salary
try:
    r = requests.post(base+'/api/merchant/staff/salary', json={
                      'employee_id': 1, 'amount': 1000}, headers={'X-Merchant-Id': '1'}, timeout=5)
    print('/salary', r.status_code, r.json())
except Exception as e:
    print('ERR salary', e)
# create campaign
try:
    r = requests.post(base+'/api/merchant/marketing/create-campaign', json={
                      'campaign_name': 'Test Camp', 'budget': 500}, headers={'X-Merchant-Id': '1'}, timeout=5)
    print('/create-campaign', r.status_code, r.json())
except Exception as e:
    print('ERR campaign', e)
# notifications get/post
try:
    r = requests.get(base+'/api/merchant/notifications/settings',
                     headers={'X-Merchant-Id': '1'}, timeout=5)
    print('/notif GET', r.status_code, r.json())
    r = requests.post(base+'/api/merchant/notifications/settings', json={
                      'email': False, 'sms': True, 'in_app': True}, headers={'X-Merchant-Id': '1'}, timeout=5)
    print('/notif POST', r.status_code, r.json())
except Exception as e:
    print('ERR notif', e)
# feedback
try:
    r = requests.post(base+'/api/merchant/feedback-ideas', json={
                      'content': 'Please add more payment methods'}, headers={'X-Merchant-Id': '1'}, timeout=5)
    print('/feedback POST', r.status_code, r.json())
    r = requests.get(base+'/api/merchant/feedback/list',
                     headers={'X-Merchant-Id': '1'}, timeout=5)
    print('/feedback LIST', r.status_code, r.json())
except Exception as e:
    print('ERR feedback', e)
