# HTTP API

All money fields are integers in minor units (cents). Identity arrives from the
gateway in `X-User-Id` and `X-User-Role` headers.

| Method | Path | Permission | Purpose |
|---|---|---|---|
| GET | `/v1/health` | none | Liveness |
| GET | `/v1/health/ready` | none | Readiness, touches the database |
| POST | `/v1/invoices` | `invoice:write` | Create and price an invoice |
| GET | `/v1/invoices/list` | `invoice:read` | Every invoice, newest first |
| GET | `/v1/invoices/{invoice_id}` | `invoice:read` | One invoice |
| POST | `/v1/invoices/{invoice_id}/captures` | `payment:capture` | Capture money against an invoice |
| GET | `/v1/invoices/{invoice_id}/payments` | `invoice:read` | Captures and refunds for an invoice |

Refunds exist in the domain and service layers but are not exposed over HTTP;
support staff issue them through an internal console.

## Errors

| Status | When |
|---|---|
| 401 | Missing or unknown principal headers |
| 403 | The role lacks the permission |
| 404 | Unknown invoice id |
| 409 | Capture is larger than the outstanding amount |
| 422 | Pricing rejected the request |
