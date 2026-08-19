import { request } from "./apiClient.js";

export function getBusinesses() {
  return request("/api/businesses");
}

export function createBusiness(data) {
  return request("/api/businesses", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
