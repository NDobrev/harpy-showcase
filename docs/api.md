# HTTP API

All money fields are integers in minor units (cents). Identity arrives from the
gateway in `X-User-Id` and `X-User-Role` headers.

| Method | Path | Permission | Purpose |
|---|---|---|---|
| GET | `/v1/health` | none | Liveness |
| GET | `/v1/health/ready` | none | Readiness, touches the database |
| POST | `/v1/invoices` | `invoice:write` | Create and price an invoice |
| GET | `/v1/invoices` | `invoice:read` | One page of invoices, newest first |
| GET | `/v1/invoices/{invoice_id}` | `invoice:read` | One invoice |
| POST | `/v1/invoices/{invoice_id}/captures` | `payment:capture` | Capture money against an invoice |
| POST | `/v1/invoices/{invoice_id}/refunds` | `refund:issue` | Refund a captured invoice |
| GET | `/v1/invoices/{invoice_id}/payments` | `invoice:read` | Captures and refunds for an invoice |

## Listing invoices

`GET /v1/invoices` takes `limit` (1–100, default 25) and an opaque `cursor`, and
answers with an envelope:

```json
{ "data": [ { "id": "inv_…" } ], "next_cursor": "MjAyNi0wOS0xN…" }
```

A `null` `next_cursor` means the last page. Cursors encode `(created_at, id)`,
so a page never repeats or skips an invoice while new ones arrive.

### Removed: `GET /v1/invoices/list`

The old route returned every invoice as a bare JSON array with no limit.
Clients must move to `GET /v1/invoices` and read `data`.

## Errors

| Status | When |
|---|---|
| 400 | Malformed pagination cursor |
| 401 | Missing or unknown principal headers |
| 403 | The role lacks the permission |
| 404 | Unknown invoice id |
| 409 | Capture or refund conflicts with the invoice state |
| 422 | Pricing rejected the request |
