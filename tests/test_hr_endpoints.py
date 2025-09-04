import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_leave_applications():
    resp = client.get("/api/leave/applications?employee_id=EMP001")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("status") == "success"
    assert isinstance(body.get("applications"), list)


def test_get_payslips():
    resp = client.get("/api/payroll/payslips?employee_id=EMP001")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("status") == "success"
    assert isinstance(body.get("payslips"), list)


def test_get_employee_status():
    resp = client.get("/api/employee/status?employee_id=EMP001")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("status") == "success"
    # data.basic_info should be present for single employee query
    assert isinstance(body.get("data"), dict)
    assert "basic_info" in body.get("data")


def test_get_attendance_history():
    resp = client.get("/api/attendance/history?employee_id=EMP001")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("status") == "success"
    assert isinstance(body.get("data"), list)
    # if there are records, ensure expected keys
    if len(body.get("data")) > 0:
        rec = body.get("data")[0]
        assert "date" in rec and "status" in rec


def test_post_apply_leave():
    payload = {
        "employee_id": "EMP001",
        "employee_name": "Test User",
        "leave_type": "Annual Leave",
        "start_date": "2025-09-10",
        "end_date": "2025-09-12",
        "days": 3,
        "reason": "Integration test"
    }
    resp = client.post("/api/leave/apply", json=payload)
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    # should return success and an application id
    assert body.get("status") == "success"
    assert "application_id" in body or "id" in body
