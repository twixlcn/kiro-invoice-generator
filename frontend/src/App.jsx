import { useState, useEffect, useCallback } from "react";
import invoiceIcon from "./assets/invoice-icon.png";
import Navbar from "./components/Navbar";
import InvoiceCard from "./components/InvoiceCard";
import InvoiceForm from "./components/InvoiceForm";
import InvoicePreview, { exportInvoicePdf } from "./components/InvoicePreview";
import ErrorBanner from "./components/ErrorBanner";
import {
  getInvoices,
  getInvoice,
  createInvoice,
  updateInvoice,
  deleteInvoice,
} from "./services/invoiceApi";

// Pre-filled default — change here to update the form default
const DEFAULT_BUSINESS = {
  name: "ACME Digital Solutions",
  address: "Davao City, Philippines",
  email: "hello@acmedigital.com",
};

const VIEW_HOME = "home";
const VIEW_CREATE = "create";
const VIEW_EDIT = "edit";
const VIEW_DETAIL = "detail";

function nextInvoiceNumber(invoices) {
  if (!invoices || invoices.length === 0) return "INV-0001";
  const nums = invoices
    .map((inv) => parseInt((inv.invoice_number || "").replace("INV-", ""), 10))
    .filter((n) => !isNaN(n));
  const max = nums.length > 0 ? Math.max(...nums) : 0;
  return `INV-${String(max + 1).padStart(4, "0")}`;
}

function fmtDateTime(iso) {
  if (!iso) return "";
  return iso.replace("T", " ");
}

export default function App() {
  const [view, setView] = useState(VIEW_HOME);
  const [invoices, setInvoices] = useState([]);
  const [detailInvoice, setDetailInvoice] = useState(null);
  const [editInvoice, setEditInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [detailError, setDetailError] = useState(null);

  const loadInvoices = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getInvoices();
      setInvoices(data);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInvoices();
  }, [loadInvoices]);

  async function handleCardClick(invoiceNumber) {
    setDetailError(null);
    try {
      const inv = await getInvoice(invoiceNumber);
      setDetailInvoice(inv);
      setView(VIEW_DETAIL);
    } catch (e) {
      setError(e);
    }
  }

  async function handleEdit(invoiceNumber) {
    setError(null);
    try {
      const inv = await getInvoice(invoiceNumber);
      setEditInvoice(inv);
      setView(VIEW_EDIT);
    } catch (e) {
      setError(e);
    }
  }

  async function handleDelete(invoiceNumber) {
    setError(null);
    try {
      await deleteInvoice(invoiceNumber);
      if (view === VIEW_DETAIL || view === VIEW_EDIT) setView(VIEW_HOME);
      await loadInvoices();
    } catch (e) {
      setError(e);
    }
  }

  async function handleCreate(payload) {
    const invoice = await createInvoice(payload);
    await loadInvoices();
    setDetailInvoice(invoice);
    setView(VIEW_DETAIL);
    return invoice;
  }

  async function handleUpdate(payload) {
    const invoice = await updateInvoice(payload.invoice_number, payload);
    await loadInvoices();
    setDetailInvoice(invoice);
    setView(VIEW_DETAIL);
    return invoice;
  }

  function goHome() {
    setView(VIEW_HOME);
    setDetailInvoice(null);
    setEditInvoice(null);
    setDetailError(null);
    setError(null);
  }

  function goBackToDetail() {
    // Cancel edit → return to detail view of the same invoice
    setView(VIEW_DETAIL);
    setEditInvoice(null);
  }

  return (
    <div className="min-h-screen bg-[#dad5e3]">
      <Navbar onHome={goHome} />

      <header className="bg-[#380B59] pb-10 pt-8 shadow-[0_1px_0_rgba(0,0,0,0.06)]">
        <div className="mx-auto max-w-6xl px-4 text-center">
          <h1 className="text-[52px] font-black uppercase tracking-[-0.05em] text-[#f2e7ff]">
            Invoice Generator
          </h1>
          <p className="mt-4 text-[24px] font-light text-[#f2e7ff]/90">
            Create polished invoices without the hassle.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        {view === VIEW_HOME && (
          <div className="fade-in">
            <div className="mb-6 flex items-center justify-between rounded-[12px] border border-[#d7cedd] bg-white px-5 py-4 shadow-[0_8px_22px_rgba(56,11,89,0.04)]">
              <div>
                <h2 className="text-[22px] font-semibold text-[#100418]">Your invoices</h2>
                <p className="text-[14px] text-[#100418]/60">Create, calculate, and save invoices.</p>
              </div>
              <button
                onClick={() => { setError(null); setView(VIEW_CREATE); }}
                className="no-print rounded-[10px] bg-[#8F67D6] px-5 py-3 text-[14px] font-semibold text-white shadow-[0_6px_14px_rgba(143,103,214,0.35)] transition hover:bg-[#7a5ec4]"
              >
                New Invoice
              </button>
            </div>

            <div className="mb-6">
              <ErrorBanner error={error} onDismiss={() => setError(null)} />
            </div>

            {loading ? (
              <p className="py-10 text-center text-sm text-[#100418]/50">Loading…</p>
            ) : invoices.length === 0 ? (
              <div className="flex min-h-[380px] items-center justify-center">
                <div className="text-center">
                  <div className="mx-auto mb-5 flex items-center justify-center">
                    <img src={invoiceIcon} alt="Invoice Generator logo" className="h-28 w-28 object-contain md:h-40 md:w-40" />
                  </div>
                  <p className="text-[16px] font-semibold text-[#7C7686]">No invoices yet</p>
                  <button
                    onClick={() => setView(VIEW_CREATE)}
                    className="mt-5 rounded-[10px] border border-[#8F67D6] px-5 py-3 text-[14px] font-semibold text-[#8F67D6] transition hover:border-[#380B59] hover:text-[#380B59]"
                  >
                    Create your first invoice
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {invoices.map((inv) => (
                  <InvoiceCard
                    key={inv.invoice_number}
                    invoice={inv}
                    onClick={() => handleCardClick(inv.invoice_number)}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {view === VIEW_CREATE && (
          <InvoiceForm
            existingInvoice={null}
            defaultBusiness={DEFAULT_BUSINESS}
            nextInvoiceNumber={nextInvoiceNumber(invoices)}
            onSave={handleCreate}
            onBack={goHome}
          />
        )}

        {view === VIEW_EDIT && editInvoice && (
          <InvoiceForm
            key={editInvoice.invoice_number}
            existingInvoice={editInvoice}
            defaultBusiness={DEFAULT_BUSINESS}
            nextInvoiceNumber={null}
            onSave={handleUpdate}
            onBack={goBackToDetail}
          />
        )}

        {view === VIEW_DETAIL && detailInvoice && (
          <div className="fade-in">
            <div className="no-print mb-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button onClick={goHome} className="text-[14px] font-medium text-[#100418]/70 transition hover:text-[#380B59]">
                  ← Go Back
                </button>
                <h1 className="text-[28px] font-semibold text-[#100418]">
                  {detailInvoice.invoice_number}
                </h1>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(detailInvoice.invoice_number)}
                  className="rounded-[8px] border border-[#8F67D6] bg-white px-4 py-2 text-[12px] font-semibold text-[#8F67D6] transition hover:bg-[#f5efff]"
                >
                  Edit
                </button>
                <button
                  onClick={() => exportInvoicePdf(detailInvoice.invoice_number)}
                  className="rounded-[8px] border border-[#8F67D6] bg-white px-4 py-2 text-[12px] font-semibold text-[#8F67D6] transition hover:bg-[#f5efff]"
                >
                  Export PDF
                </button>
                <button
                  onClick={() => {
                    if (window.confirm(`Delete invoice ${detailInvoice.invoice_number}? This cannot be undone.`)) {
                      handleDelete(detailInvoice.invoice_number);
                    }
                  }}
                  className="rounded-[8px] bg-[#8F67D6] px-4 py-2 text-[12px] font-semibold text-white transition hover:bg-[#7a5ec4]"
                >
                  Delete
                </button>
              </div>
            </div>

            {detailInvoice.updated_at && detailInvoice.updated_at !== detailInvoice.created_at && (
              <p className="no-print mb-4 text-xs text-[#100418]/55">
                Last updated {fmtDateTime(detailInvoice.updated_at)}
              </p>
            )}

            <ErrorBanner error={detailError} onDismiss={() => setDetailError(null)} />
            <InvoicePreview invoice={detailInvoice} />
          </div>
        )}
      </main>
    </div>
  );
}
