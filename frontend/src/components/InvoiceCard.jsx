function fmtDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function InvoiceCard({ invoice, onClick, onEdit, onDelete }) {
  function handleEdit(e) {
    e.stopPropagation();
    if (onEdit) onEdit(invoice.invoice_number);
  }

  function handleDelete(e) {
    e.stopPropagation();
    if (!onDelete) return;
    if (window.confirm(`Delete invoice ${invoice.invoice_number}? This cannot be undone.`)) {
      onDelete(invoice.invoice_number);
    }
  }

  return (
    <div
      onClick={onClick}
      className="fade-in flex w-full items-center gap-4 rounded-[12px] border border-[#d7cde5] bg-white p-4 shadow-[0_1px_0_rgba(56,11,89,0.05)] transition-all duration-200 hover:shadow-[0_4px_14px_rgba(56,11,89,0.08)]"
    >
      <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 border-[#8f67d6] bg-[#f5efff] text-base font-bold text-[#8f67d6]">
        ₱
        <span className="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full border border-[#8f67d6] bg-[#f3e9ff] text-[9px] font-bold text-[#8f67d6]">
          ✓
        </span>
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate text-[16px] font-semibold text-[#100418]">
          {invoice.invoice_number ? `Invoice #${invoice.invoice_number}` : "Invoice"}
        </p>
        <p className="text-[12px] text-[#100418]/70">Created {fmtDate(invoice.created_at)}</p>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            if (onEdit) handleEdit(e);
          }}
          className="rounded-[8px] border border-[#8f67d6] bg-white px-4 py-2 text-[12px] font-medium text-[#8f67d6] transition-colors hover:bg-[#f5efff]"
        >
          Edit
        </button>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            if (onDelete) handleDelete(e);
          }}
          className="rounded-[8px] border border-[#8f67d6] bg-white px-4 py-2 text-[12px] font-medium text-[#8f67d6] transition-colors hover:bg-[#f5efff]"
        >
          Delete
        </button>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            if (onClick) onClick();
          }}
          className="rounded-[8px] border border-[#8f67d6] bg-[#f6f0ff] px-4 py-2 text-[12px] font-medium text-[#8f67d6] transition-colors hover:bg-[#efe3ff]"
        >
          Export as PDF
        </button>
      </div>
    </div>
  );
}
