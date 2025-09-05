import requests

BASE = "http://127.0.0.1:8000"


def test_promotions_endpoint():
    r = requests.get(BASE + '/api/merchant/marketing/promotions',
                     params={'merchant_id': 'MERCH_TEST'})
    assert r.status_code == 200
    j = r.json()
    assert 'data' in j
    data = j['data']
    assert 'campaigns' in data and isinstance(data['campaigns'], list)


def test_notifications_endpoint():
    r = requests.get(BASE + '/api/merchant/notifications',
                     params={'merchant_id': 'MERCH_TEST'})
    assert r.status_code == 200
    j = r.json()
    assert 'data' in j
    data = j['data']
    # should contain at least one of the expected keys
    assert any(k in data for k in [
               'pending_leave_requests', 'pending_shift_changes', 'payment_settlement', 'head_office_messages'])
