# ProductX API Documentation

## Overview
ProductX is a REST API for managing customer data, orders, and inventory in real time.
Base URL: `https://api.productx.io/v2`
All requests must include an `Authorization: Bearer <token>` header.

## Authentication
Tokens are issued via the `/auth/token` endpoint using OAuth 2.0 client credentials.
Tokens expire after 24 hours. Refresh using `/auth/refresh`.

## Endpoints

### GET /customers
Returns a paginated list of customers.
**Query params:** `page` (default 1), `limit` (default 20, max 100), `search` (name or email).
**Response:** `{ data: [...], total: 450, page: 1, limit: 20 }`

### POST /customers
Create a new customer.
**Body:** `{ name, email, phone?, address? }`
**Returns:** the created customer object with `id`.

### GET /orders/{id}
Fetch a single order by ID.
**Returns:** order object with `status`, `items`, `total`, `created_at`.

### POST /orders
Place a new order.
**Body:** `{ customer_id, items: [{ product_id, quantity }] }`
**Returns:** order object with `id` and `status: pending`.

### GET /inventory/{product_id}
Check stock level for a product.
**Returns:** `{ product_id, sku, stock: 142, reserved: 10, available: 132 }`

## Rate Limits
- Free tier: 100 requests/minute
- Pro tier: 1000 requests/minute
- Enterprise: custom limits
Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Error Codes
| Code | Meaning                  |
|------|--------------------------|
| 400  | Bad request / validation |
| 401  | Invalid or expired token |
| 403  | Insufficient permissions |
| 404  | Resource not found       |
| 429  | Rate limit exceeded      |
| 500  | Internal server error    |

## Webhooks
Subscribe to events via `/webhooks`. Supported events:
- `order.created`, `order.fulfilled`, `order.cancelled`
- `inventory.low` (triggered when stock < threshold)

Webhook payloads are signed with HMAC-SHA256. Verify using your webhook secret.

## SDKs
Official SDKs available for Python, Node.js, and Go.
Install Python SDK: `pip install productx-sdk`
