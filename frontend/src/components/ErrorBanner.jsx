export default function ErrorBanner({ error, onDismiss }) {
  if (!error) return null;

  const friendly = friendlyMessage(error);

  return (
    <div className="mb-4 flex items-start justify-between rounded-[10px] border border-[#f2c7cf] bg-[#fff2f4] px-4 py-3">
      <div>
        <p className="text-sm text-[#8b2347]">{friendly}</p>
        {error.requestId && (
          <p className="mt-1 text-xs text-[#8b2347]/70">Request ID: {error.requestId}</p>
        )}
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="ml-4 text-lg leading-none text-[#8b2347] hover:text-[#731c39]">
          ×
        </button>
      )}
    </div>
  );
}

function friendlyMessage(error) {
  if (!error) return "";
  if (error.status === 0) return "Unable to connect to the server. Please make sure the backend is running.";
  if (error.status === 404) return `Invoice not found. ${error.message}`;
  if (error.status === 409) return `Duplicate invoice number. ${error.message}`;
  if (error.status === 422) return error.message || "Validation failed. Please check the information entered and try again.";
  if (error.status === 500) return `Server error. Please try again or check the logs.`;
  return error.message || "An unexpected error occurred.";
}
