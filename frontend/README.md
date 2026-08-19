# Invoice Generator — Frontend

React + Vite + TailwindCSS, plain JavaScript.

## Views

1. **Home** — invoice list, empty state, delete with confirm
2. **Create Invoice** — business/customer picker (select existing or add new inline), form with live item totals, calculate preview, save
3. **Invoice Detail** — full preview, delete

## API Layer

`src/services/apiClient.js` holds the shared `fetch()` wrapper (`request()`, `ApiError`) — every API module builds on it:
- `invoiceApi.js` — invoices
- `businessApi.js` — businesses
- `customerApi.js` — customers

Tax conversion happens in `invoiceApi.js`:
- UI stores tax as **percent** (12)
- API expects **decimal** (0.12)
- `toApiPayload()` converts out; `fromApiInvoice()` converts back in

Invoices are created/updated with `business_id`/`customer_id`; the API still responds with full nested `business`/`customer` objects, so `InvoicePreview.jsx` and `InvoiceCard.jsx` read them the same way either way.

## Error Handling

Every API function throws `ApiError` carrying `status`, `message`, `requestId`.  
`ErrorBanner.jsx` shows a friendly message + the `request_id` in grey text.  
Copy the request ID and grep the backend logs to trace any failure.

## Running

```bash
npm install
npm run dev
```

App: http://localhost:5173  
Requires backend at `VITE_API_URL` (default: `http://localhost:8000`)
