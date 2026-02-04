import { useState, useEffect, type FormEvent } from "react";
import { fetchLocations, searchItems } from "./api";
import type { LocationsResponse, SearchResult } from "./types";
import "./App.css";

function App() {
  const [locations, setLocations] = useState<LocationsResponse | null>(null);
  const [sido, setSido] = useState("");
  const [sigungu, setSigungu] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    fetchLocations()
      .then(setLocations)
      .catch(() => setError("지역 정보를 불러오는데 실패했습니다."));
  }, []);

  const handleSidoChange = (value: string) => {
    setSido(value);
    setSigungu("");
  };

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      setResults([]);
      setError("검색어를 입력해주세요.");
      return;
    }
    if (loading) return;

    setLoading(true);
    setError("");
    setHasSearched(true);
    try {
      const response = await searchItems(query, sido, sigungu);
      setResults(response.results);
    } catch {
      setResults([]);
      setError("검색에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const sigunguOptions = sido && locations ? locations.sigungu[sido] || [] : [];

  return (
    <div className="container">
      <h1>대형폐기물 품목 검색</h1>
      <p className="description">
        버리려는 물건을 검색하면 유사한 대형폐기물 품목과 수수료를 안내합니다.
      </p>

      <form onSubmit={handleSearch} className="search-form">
        <div className="filters">
          <select
            value={sido}
            onChange={(e) => handleSidoChange(e.target.value)}
            className="select"
          >
            <option value="">시도 선택</option>
            {locations?.sido.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          <select
            value={sigungu}
            onChange={(e) => setSigungu(e.target.value)}
            className="select"
            disabled={!sido}
          >
            <option value="">시군구 선택</option>
            {sigunguOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div className="search-row">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="예: 티비, 소파, 냉장고"
            className="search-input"
          />
          <button type="submit" disabled={loading} className="search-button">
            {loading ? "검색 중..." : "검색"}
          </button>
        </div>
      </form>

      {error && <div className="error">{error}</div>}

      {hasSearched && results.length === 0 && !loading && !error && (
        <div className="results">
          <div className="empty-state">
            <div className="empty-state-icon">🔍</div>
            <p>검색 결과가 없습니다.</p>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="results">
          <h2>검색 결과</h2>
          <ul className="result-list">
            {results.map((item, index) => (
              <li
                key={`${item.name}-${item.category}-${item.sigungu}-${item.sido}-${index}`}
                className="result-item"
              >
                <div className="result-header">
                  <span className="item-name">{item.name}</span>
                  <span className="similarity">
                    {(item.similarity * 100).toFixed(1)}% 일치
                  </span>
                </div>
                <div className="result-details">
                  <span className="category">{item.category}</span>
                  {item.spec && <span className="spec">{item.spec}</span>}
                </div>
                <div className="result-footer">
                  <span className="location">
                    {item.sido} {item.sigungu}
                  </span>
                  <span className="fee">
                    {item.fee > 0 ? `${item.fee.toLocaleString()}원` : "무료"}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
