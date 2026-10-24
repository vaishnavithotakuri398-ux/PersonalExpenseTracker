
import pytest
import app as expense_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        expense_app,
        "DB_NAME",
        str(tmp_path / "test.db")
    )

    expense_app.init_db()
    expense_app.app.config["TESTING"] = True

    with expense_app.app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_expense(client):
    response = client.post("/expenses", json={
        "title": "Lunch",
        "amount": 150,
        "category": "Food"
    })

    assert response.status_code == 201


def test_get_expenses(client):
    client.post("/expenses", json={
        "title": "Bus",
        "amount": 30,
        "category": "Travel"
    })

    response = client.get("/expenses")

    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_invalid_amount(client):
    response = client.post("/expenses", json={
        "title": "Lunch",
        "amount": -10,
        "category": "Food"
    })

    assert response.status_code == 400


def test_total(client):
    client.post("/expenses", json={
        "title": "Lunch",
        "amount": 150,
        "category": "Food"
    })

    response = client.get("/total")

    assert response.get_json()["total"] == 150.0
