import type { LocationsResponse, SearchResponse } from "./types";

const API_BASE = "http://localhost:8000";

export async function fetchLocations(): Promise<LocationsResponse> {
  const res = await fetch(`${API_BASE}/api/locations`);
  if (!res.ok) throw new Error("Failed to fetch locations");
  return res.json();
}

export async function searchItems(
  query: string,
  sido?: string,
  sigungu?: string
): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, sido: sido || null, sigungu: sigungu || null }),
  });
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}
