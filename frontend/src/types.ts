export interface SearchResult {
  name: string;
  category: string;
  spec: string;
  fee: number;
  similarity: number;
  sido: string;
  sigungu: string;
}

export interface SearchResponse {
  results: SearchResult[];
}

export interface LocationsResponse {
  sido: string[];
  sigungu: Record<string, string[]>;
}
