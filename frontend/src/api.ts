import type { LocationsResponse, SearchResponse } from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/+$/, "");

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
  const params = new URLSearchParams({ query });
  if (sido) params.append("sido", sido);
  if (sigungu) params.append("sigungu", sigungu);
  const res = await fetch(`${API_BASE}/api/search?${params}`);
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}
