from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_homepage_loads():
    response = client.get('/')
    assert response.status_code == 200
    assert 'Northstar Market' in response.text


def test_products_endpoint_returns_data():
    response = client.get('/api/products')
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) > 0
    assert 'name' in payload[0]


def test_categories_endpoint_returns_data():
    response = client.get('/api/categories')
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 5
    assert payload[0]['name'] == 'Electronics'


def test_checkout_requires_items():
    bad_request = {
        'customer_name': 'Jane Doe',
        'email': 'jane@example.com',
        'address': '123 Market St',
        'city': 'San Jose',
        'payment_method': 'Card',
        'items': [],
    }
    response = client.post('/api/orders/checkout', json=bad_request)
    assert response.status_code == 400


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert payload['app'] == 'Northstar Market'


def test_stats_endpoint():
    response = client.get('/api/stats')
    assert response.status_code == 200
    payload = response.json()
    assert payload['product_count'] > 0
    assert payload['category_count'] > 0
    assert payload['order_count'] >= 0
