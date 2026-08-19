/**
 * Shared fetch wrapper — every API module (invoice/business/customer) uses this.
 */
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

export async function request(path, options = {}) {
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
      message = body.message || body.detail?.[0]?.msg || message;
    } catch (_) {}
    throw new ApiError(response.status, message, requestId);
  }

  return response.json();
}
