import importlib
import io
import sys
from types import SimpleNamespace

import pytest

from classes import Bill, Payee


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("SPLITMYBILL_SESSION_DIR", str(tmp_path / "sessions"))
    monkeypatch.delenv("MINDEE_API_KEY", raising=False)
    sys.modules.pop("project", None)
    module = importlib.import_module("project")
    module.app.config.update(TESTING=True)
    yield module
    sys.modules.pop("project", None)


def test_paxcount_rejects_non_integer():
    with pytest.raises(ValueError):
        Bill().paxcount = "two"


def test_bill_rejects_unknown_payee():
    with pytest.raises(ValueError):
        Bill().addItem({"serial": 0, "name": "Meal", "payee": "unknown", "price": 3})


def test_removing_item_keeps_serials_contiguous():
    bill = Bill()
    for index in range(3):
        bill.addItem({"serial": index, "name": "Meal", "payee": None, "price": 3})
    bill.removeItem(1)
    assert [item["serial"] for item in bill.items] == [0, 1]


def test_payee_total_accepts_numeric_prices_and_rounds():
    payee = Payee("Fictional diner")
    payee.addItem({"serial": 0, "name": "Meal", "price": "3.125"})
    assert payee.sum == 3.12
    with pytest.raises(ValueError):
        payee.sum = "invalid"


def start_bill(client):
    assert client.get("/pax_receipt").status_code == 200
    assert client.post("/pax_receipt", data={"paxcount": "2"}).status_code == 302
    assert client.post("/naming", data={"name1": "Diner A", "name2": "Diner B"}).status_code == 302


def test_actual_manual_flow_calculates_and_resets(project):
    client = project.app.test_client()
    start_bill(client)
    client.post("/add_item", data={"item-name": "Meal", "item-price": "10", "item-payee": "Diner A"})
    response = client.post("/items_list", data={"gst": "on", "svccharge": "on", "discount": "2"})
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["bill"].payees["Diner A"].sum == 10.99
    assert client.get("/summary").status_code == 200
    assert client.post("/summary").status_code == 302
    with client.session_transaction() as session:
        assert "bill" not in session


def test_recalculation_does_not_double_count(project):
    client = project.app.test_client()
    start_bill(client)
    client.post("/add_item", data={"item-name": "Meal", "item-price": "10", "item-payee": "Diner A"})
    for _ in range(2):
        client.post("/items_list", data={"discount": "0"})
    with client.session_transaction() as session:
        assert session["bill"].payees["Diner A"].sum == 10


def test_ocr_without_key_does_not_call_provider(project, monkeypatch):
    def forbidden_provider(*args, **kwargs):
        raise AssertionError("OCR provider must not be called without configuration")
    monkeypatch.setattr(project, "Client", forbidden_provider)
    client = project.app.test_client()
    client.get("/pax_receipt")
    response = client.post("/pax_receipt", data={"paxcount": "2", "file": (io.BytesIO(b"fictional receipt"), "receipt.png")}, content_type="multipart/form-data")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/pax_receipt")


def test_ocr_adapter_uses_environment_key_and_imports_line_items(project, monkeypatch):
    monkeypatch.setenv("MINDEE_API_KEY", "fictional-test-key")
    class FakeClient:
        def __init__(self, *, api_key):
            assert api_key == "fictional-test-key"
        def source_from_bytes(self, content, filename):
            return (content, filename)
        def parse(self, product_type, document):
            prediction = SimpleNamespace(line_items=[SimpleNamespace(description="Meal",quantity=2,unit_price=3,total_amount=6)], taxes=[])
            return SimpleNamespace(document=SimpleNamespace(inference=SimpleNamespace(prediction=prediction)))
    monkeypatch.setattr(project, "Client", FakeClient)
    client = project.app.test_client()
    client.get("/pax_receipt")
    response = client.post("/pax_receipt", data={"paxcount": "2", "file": (io.BytesIO(b"fictional receipt"), "receipt.png")}, content_type="multipart/form-data")
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert len(session["bill"].items) == 2
        assert sum(item["price"] for item in session["bill"].items) == 6
