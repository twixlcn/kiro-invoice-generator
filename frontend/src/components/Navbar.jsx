import invoiceIcon from "../assets/invoice-icon.png";

export default function Navbar({ onHome }) {
  return (
    <nav className="no-print bg-[#503480] px-5 py-2 shadow-[0_1px_0_rgba(0,0,0,0.08)]">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <button
          onClick={onHome}
          className="flex items-center gap-2 text-[14px] font-medium text-[#C5A3FF] transition-opacity hover:opacity-90"
        >
          <img src={invoiceIcon} alt="Invoice Generator logo" className="h-10 w-10 object-contain" />
          <span>Invoice Generator</span>
        </button>

        <span className="text-[11px] italic font-medium text-[#C5A3FF]">Powered by Kiro</span>
      </div>
    </nav>
  );
}
