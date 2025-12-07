# Order Management API

E-commerce order management service built with FastAPI and SQLite.

## Features

- Create orders with customer, shipping address, and items
- Automatic warehouse selection based on inventory availability and proximity
- Payment processing integration (mocked)
- Address geocoding (mocked)

## Setup

### 1. Create and activate virtual environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Seed the database (optional)

```bash
python seed_data.py
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### POST /orders

Create a new order.

**Request Body:**

```json
{
  "customer_id": 1,
  "shipping_address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94102",
    "country": "USA"
  },
  "credit_card": {
    "number": "4111111111111111",
    "expiry": "12/25",
    "cvv": "123"
  },
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 2, "quantity": 1}
  ]
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "customer_id": 1,
  "warehouse": {
    "id": 1,
    "name": "West Coast Warehouse",
    "address": "123 Tech Blvd, San Francisco, CA 94102, USA"
  },
  "shipping_address": "123 Main St, San Francisco, CA 94102, USA",
  "total_amount": 2029.97,
  "payment_id": "pay_abc123def456",
  "status": "confirmed",
  "created_at": "2025-12-07T12:00:00",
  "items": [
    {
      "product_id": 1,
      "product_name": "Laptop",
      "quantity": 2,
      "unit_price": 999.99
    },
    {
      "product_id": 2,
      "product_name": "Wireless Mouse",
      "quantity": 1,
      "unit_price": 29.99
    }
  ]
}
```

**Error Responses:**

- `400 Bad Request`: No warehouse has all requested products
- `402 Payment Required`: Payment was declined
- `404 Not Found`: Customer or product not found

### GET /health

Health check endpoint.

## Business Logic

### Warehouse Selection

1. Find all warehouses that have ALL requested products in sufficient quantity
2. If multiple warehouses qualify, select the one closest to the shipping address (using Haversine distance)
3. If no warehouse can fulfill the order, return an error

### Mocked Services

**Geocoding**: Uses a deterministic hash of the address to generate consistent lat/lng coordinates within the US continental range.

**Payment**: Cards starting with "0" are declined (for testing failure scenarios). All other cards are approved.

## Seed Data

The seed script creates:

- **3 Customers**: Alice, Bob, Carol
- **5 Products**: Laptop ($999.99), Mouse ($29.99), USB-C Hub ($49.99), Monitor Stand ($79.99), Keyboard ($149.99)
- **3 Warehouses**:
  - West Coast (San Francisco) - has all products
  - Central (Dallas) - missing Keyboard
  - East Coast (New York) - has all products, limited laptop stock

