import requests
import time


BASE = 'http://127.0.0.1:8000'
HEADERS = {'Content-Type': 'application/json', 'X-Merchant-Id': 'MERCH_TEST'}


def test_submit_feedback_and_list():
    # create a unique feedback payload
    content = f"Automated test feedback {int(time.time())}"
    resp = requests.post(f"{BASE}/api/merchant/feedback-ideas",
                         json={"content": content}, headers=HEADERS, timeout=5)
    assert resp.status_code == 200
    j = resp.json()
    assert j.get('status') == 'success'
    assert 'data' in j and isinstance(j['data'], dict)
    created = j['data']
    assert created.get('content') == content

    # fetch list and ensure the created feedback is present
    resp2 = requests.get(
        f"{BASE}/api/merchant/feedback/list", headers=HEADERS, timeout=5)
    assert resp2.status_code == 200
    j2 = resp2.json()
    assert j2.get('status') == 'success'
    data = j2.get('data') or []
    # find an entry with the same content
    matches = [f for f in data if f.get('content') == content]
    assert len(
        matches) >= 1, f"Submitted feedback not found in list: {content}"
