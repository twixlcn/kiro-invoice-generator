import { request } from "./apiClient.js";

export function getCustomers() {
  return request("/api/customers");
}

export function createCustomer(data) {
  return request("/api/customers", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
