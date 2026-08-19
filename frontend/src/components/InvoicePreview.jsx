/**
 * InvoicePreview — shared by the Calculate result and the Detail view.
 *
 * exportInvoicePdf(invoiceNumber):
 *   Sets document.title to the invoice number so browsers default the
 *   PDF filename to e.g. "INV-0001.pdf", calls window.print(), then
 *   restores the title via onafterprint (with a 1 s setTimeout fallback).
 *   No library, no backend call — pure browser print dialog.
 */

function fmt(amount) {
  return "₱" + Number(amount).toLocaleString("en-PH", { minimumFractionDigits: 2 });
}

export function exportInvoicePdf(invoiceNumber) {
  const originalTitle = document.title;

  function restore() {
    document.title = originalTitle;
  }

  document.title = invoiceNumber;
  window.onafterprint = restore;
  setTimeout(restore, 1000);
  window.print();
}

export default function InvoicePreview({ invoice }) {
  if (!invoice) return null;

  const { invoice_number, invoice_date, due_date, business, customer, items, totals, tax_rate, notes, payment_method } = invoice;
  const taxPct = typeof tax_rate === "number" ? (tax_rate > 1 ? tax_rate : tax_rate * 100) : 0;
  const hasNotes = Boolean(notes && notes.trim());
  const hasPaymentMethod = Boolean(payment_method && payment_method.trim());

  return (
    <div
      id="invoice-print-area"
      className="fade-in mx-auto max-w-3xl rounded-[18px] border border-[#d7cedd] bg-white p-8 shadow-[0_8px_22px_rgba(56,11,89,0.06)]"
    >
      <div className="mb-6 border-b border-[#e9dff4] pb-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="mb-1 text-[11px] font-medium uppercase tracking-[0.14em] text-[#8f67d6]">Invoice</p>
            <p className="text-[26px] font-bold text-[#100418]">{invoice_number}</p>
          </div>
        </div>

        <div className="mt-5 flex flex-col gap-4 sm:flex-row sm:justify-between">
          <div>
            <p className="font-semibold text-[#100418]">{business?.name}</p>
            <p className="text-sm text-[#100418]/70">{business?.address}</p>
            <p className="text-sm text-[#100418]/70">{business?.email}</p>
          </div>

          <div className="sm:text-right">
            <p className="mb-1 text-[11px] font-medium uppercase tracking-[0.14em] text-[#8f67d6]">Bill To</p>
            <p className="font-semibold text-[#100418]">{customer?.name}</p>
            <p className="text-sm text-[#100418]/70">{customer?.email}</p>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-6 text-sm text-[#100418]/75">
          <span>Invoice Date: <strong>{invoice_date}</strong></span>
          <span>Due Date: <strong>{due_date}</strong></span>
        </div>
      </div>

      <table className="mb-6 w-full text-sm">
        <thead>
          <tr className="bg-[#f5efff] text-[11px] font-semibold uppercase tracking-[0.12em] text-[#380b59]">
            <th className="px-3 py-3 text-left">Description</th>
            <th className="px-3 py-3 text-center">Qty</th>
            <th className="px-3 py-3 text-right">Price</th>
            <th className="px-3 py-3 text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          {(items || []).map((item, i) => (
            <tr key={i} className="border-b border-[#e9dff4]">
              <td className="px-3 py-3 text-[#100418]">{item.description}</td>
              <td className="px-3 py-3 text-center text-[#100418]/75">{item.quantity}</td>
              <td className="px-3 py-3 text-right text-[#100418]/75">{fmt(item.unit_price)}</td>
              <td className="px-3 py-3 text-right font-semibold text-[#100418]">
                {fmt(item.item_total ?? (item.quantity * item.unit_price))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex justify-end">
        <div className="w-64 space-y-2 text-sm text-[#100418]/80">
          <div className="flex justify-between">
            <span>Subtotal</span>
            <span>{fmt(totals?.subtotal ?? 0)}</span>
          </div>
          <div className="flex justify-between">
            <span>Discount</span>
            <span>-{fmt(totals?.discount ?? 0)}</span>
          </div>
          <div className="flex justify-between">
            <span>Tax ({taxPct}%)</span>
            <span>{fmt(totals?.tax ?? 0)}</span>
          </div>
          <div className="mt-3 flex justify-between border-t border-[#380b59]/20 pt-3 text-[20px] font-semibold text-[#100418]">
            <span>Total</span>
            <span>{fmt(totals?.total ?? 0)}</span>
          </div>
        </div>
      </div>

      {(hasNotes || hasPaymentMethod) && (
        <div className="mt-8 border-t border-[#e9dff4] pt-4 space-y-3 text-sm text-[#100418]/75">
          {hasNotes && (
            <div>
              <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#380b59]">Notes</p>
              <p>{notes}</p>
            </div>
          )}
          {hasPaymentMethod && (
            <div>
              <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#380b59]">Payment Method</p>
              <p>{payment_method}</p>
            </div>
          )}
        </div>
      )}

      <p className="mt-8 border-t border-[#e9dff4] pt-4 text-center text-sm text-[#100418]/55">
        Thank you for your business!
      </p>
    </div>
  );
}
