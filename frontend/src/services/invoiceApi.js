/**
 * Invoice-specific API calls.
 *
 * Tax conversion rule (single source of truth):
 *   UI stores tax as percent (12).
 *   API expects decimal (0.12).
 *   Convert OUT when sending, convert BACK IN when receiving.
 */
import { request, ApiError } from "./apiClient.js";

const BASE_URL = import.meta.env.VITE_API_URL;

export class ApiError extends Error {
  constructor(status, message, requestId) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.message = message;
    this.requestId = requestId;
  }
}

function parseValidationMessage(body) {
  if (!body) return "Validation failed. Please check the information entered and try again.";

  if (typeof body.message === "string" && body.message.trim()) {
    return body.message;
  }

  if (Array.isArray(body.detail)) {
    const parts = body.detail
      .map((entry) => {
        if (typeof entry === "string") return entry;
        if (entry?.msg) {
          const loc = Array.isArray(entry.loc) ? entry.loc.slice(1).join(".") : "";
          const cleaned = entry.msg.replace(/^Value error, /i, "");
          if (loc) return `${loc}: ${cleaned}`;
          return cleaned;
        }
        return null;
      })
      .filter(Boolean);

    if (parts.length) return parts.join(" | ");
  }

  if (typeof body.detail === "string" && body.detail.trim()) {
    return body.detail;
  }

  return "Validation failed. Please check the information entered and try again.";
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkErr) {
    throw new ApiError(0, "Cannot reach the server. Is the backend running?", null);
  }

  const requestId = response.headers.get("x-request-id");

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      message = parseValidationMessage(body);
    } catch (_) {}
    throw new ApiError(response.status, message, requestId);
  }

  return response.json();
}

/** Convert invoice payload: percent → decimal for tax_rate */
function toApiPayload(data) {
  return {
    ...data,
    tax_rate: data.tax_rate / 100,
  };
}

/** Convert invoice response: decimal → percent for tax_rate */
function fromApiInvoice(inv) {
  if (!inv) return inv;
  return {
    ...inv,
    tax_rate: inv.tax_rate * 100,
  };
}

export function getHealth() {
  return request("/api/health");
}

export function getInvoices() {
  return request("/api/invoices");
}

export function getInvoice(invoiceNumber) {
  return request(`/api/invoices/${encodeURIComponent(invoiceNumber)}`).then(fromApiInvoice);
}

export function calculateInvoice(data) {
  return request("/api/invoices/calculate", {
    method: "POST",
    body: JSON.stringify(toApiPayload(data)),
  });
}

export function createInvoice(data) {
  return request("/api/invoices", {
    method: "POST",
    body: JSON.stringify(toApiPayload(data)),
  }).then(fromApiInvoice);
}

export function updateInvoice(invoiceNumber, data) {
  return request(`/api/invoices/${encodeURIComponent(invoiceNumber)}`, {
    method: "PUT",
    body: JSON.stringify(toApiPayload(data)),
  }).then(fromApiInvoice);
}

export function deleteInvoice(invoiceNumber) {
  return request(`/api/invoices/${encodeURIComponent(invoiceNumber)}`, {
    method: "DELETE",
  });
}
