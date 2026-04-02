from __future__ import annotations

import httpx
import pytest


# helper
async def register_and_login(client: httpx.AsyncClient, email: str) -> dict[str, str]:
    """Register a user and return auth headers."""
    await client.post("/auth/register", json={"email": email, "password": "password123"})
    r = await client.post("/auth/login", json={"email": email, "password": "password123"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Register → login → create category → create transaction → verify


@pytest.mark.asyncio
async def test_full_transaction_flow(client: httpx.AsyncClient) -> None:
    headers = await register_and_login(client, "flow1@test.com")

    r = await client.post("/categories", json={"name": "Salary", "type": "income"}, headers=headers)
    assert r.status_code == 201
    category_id = r.json()["id"]

    r = await client.post(
        "/transactions",
        json={
            "amount": "5000.00",
            "type": "income",
            "date": "2024-03-01",
            "category_id": category_id,
        },
        headers=headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["amount"] == "5000.00"
    assert body["category_name"] == "Salary"
    assert body["type"] == "income"

    # Verify it appears in the list
    r = await client.get("/transactions", headers=headers)
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["data"][0]["amount"] == "5000.00"


# Create transaction with invalid category ID → 404


@pytest.mark.asyncio
async def test_create_transaction_with_invalid_category_returns_404(
    client: httpx.AsyncClient,
) -> None:
    headers = await register_and_login(client, "flow2@test.com")

    r = await client.post(
        "/transactions",
        json={
            "amount": "100.00",
            "type": "income",
            "date": "2024-03-01",
            "category_id": 9999,
        },
        headers=headers,
    )
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"
    assert r.json()["message"] == "Category not found"


# Access protected route without token → 401


@pytest.mark.asyncio
async def test_protected_route_without_token_returns_401(client: httpx.AsyncClient) -> None:
    for path in ["/transactions", "/categories", "/summary"]:
        r = await client.get(path)
        assert r.status_code == 401, f"Expected 401 for {path}, got {r.status_code}"
        assert r.json()["error"] == "unauthorized"


# GET /summary totals are correct after multiple transactions


@pytest.mark.asyncio
async def test_summary_returns_correct_monthly_totals(client: httpx.AsyncClient) -> None:
    headers = await register_and_login(client, "flow4@test.com")

    # Create categories
    r = await client.post("/categories", json={"name": "Salary", "type": "income"}, headers=headers)
    income_cat = r.json()["id"]

    r = await client.post("/categories", json={"name": "Food", "type": "expense"}, headers=headers)
    expense_cat = r.json()["id"]

    # Two income, one expense — all in 2024-03
    for amount in ("3000.00", "2000.00"):
        await client.post(
            "/transactions",
            json={
                "amount": amount,
                "type": "income",
                "date": "2024-03-01",
                "category_id": income_cat,
            },
            headers=headers,
        )
    await client.post(
        "/transactions",
        json={
            "amount": "800.00",
            "type": "expense",
            "date": "2024-03-15",
            "category_id": expense_cat,
        },
        headers=headers,
    )

    r = await client.get("/summary?month=2024-03", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    summary = data[0]
    assert summary["month"] == "2024-03"
    assert float(summary["total_income"]) == 5000.00
    assert float(summary["total_expense"]) == 800.00
    assert float(summary["net_balance"]) == 4200.00
