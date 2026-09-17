# Pricing

Money is an integer number of cents everywhere. Rounding is half to even, so
repeatedly pricing similar invoices does not drift upward.

## Order of operations

1. Sum the line items into the subtotal.
2. Compute the invoice discount from the subtotal (capped at 40% without approval).
3. Prorate that discount across the lines by amount, largest remainder first.
4. Tax each line on its discounted amount.
5. Total = subtotal − discount + the sum of line taxes.

Because step 4 follows step 3, a discount reduces both what the customer owes
and the tax charged on it.

## Worked example

Three seats at 19.99 plus priority support at 49.00, `US-CA` (8.75%), 10% off:

| Line | Amount | Discount | Taxable | Tax |
|---|---:|---:|---:|---:|
| Team seat ×3 | 5997 | 600 | 5397 | 472 |
| Priority support | 4900 | 490 | 4410 | 386 |
| **Invoice** | **10897** | **1090** | **9807** | **858** |

Total: 10897 − 1090 + 858 = **10665**.

The discount allocation is 599.76 and 490.24 before rounding; both floor, and
the single leftover cent goes to the larger line.

## Rounding is applied per line

Line taxes are rounded individually and then summed, so an invoice total can
differ by a cent or two from tax computed on the invoice subtotal. The line
breakdown always reconciles with the invoice totals — that is the invariant
worth preserving.
