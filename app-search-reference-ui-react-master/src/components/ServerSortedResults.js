import React, { useState, useEffect } from "react";
import ProductCard from "./ProductCard";

export default function ServerSortedResults({ results, searchTerm, current, resultsPerPage, sortMode, minPrice, maxPrice, color, size }) {
  const [serverResults, setServerResults] = useState(null);
  const [loadingServer, setLoadingServer] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const hasPriceFilter = (minPrice !== undefined && minPrice !== null && String(minPrice).trim() !== '') ||
      (maxPrice !== undefined && maxPrice !== null && String(maxPrice).trim() !== '');
    const hasColorFilter = (color !== undefined && color !== null && String(color).trim() !== '');
    const hasSizeFilter = (size !== undefined && size !== null && String(size).trim() !== '');
    if (!sortMode && !hasPriceFilter && !hasColorFilter && !hasSizeFilter) {
      setServerResults(null);
      return () => { cancelled = true; };
    }
    const page = current || 1;
    const per_page = resultsPerPage || 20;
    const q = searchTerm || '';
    const paramsObj = { q, page: String(page), per_page: String(per_page) };
    if (sortMode) paramsObj.sort = sortMode;
    if (color !== undefined && color !== null && String(color).trim() !== '') paramsObj.color = String(color);
    if (size !== undefined && size !== null && String(size).trim() !== '') paramsObj.size = String(size);
    if (minPrice !== undefined && minPrice !== null && String(minPrice).trim() !== '') paramsObj.min_price = String(minPrice);
    if (maxPrice !== undefined && maxPrice !== null && String(maxPrice).trim() !== '') paramsObj.max_price = String(maxPrice);
    const params = new URLSearchParams(paramsObj);
    const url = `http://localhost:8000/search?${params.toString()}`;
    setLoadingServer(true);
    fetch(url)
      .then(r => r.ok ? r.json() : Promise.reject(r))
      .then(data => {
        if (cancelled) return;
        const hits = data.hits || [];
        const mapped = hits.map(h => ({ _source: h }));
        setServerResults(mapped);
      })
      .catch(() => {
        if (!cancelled) setServerResults(null);
      })
      .finally(() => { if (!cancelled) setLoadingServer(false); });

    return () => { cancelled = true; };
  }, [sortMode, searchTerm, current, resultsPerPage, minPrice, maxPrice, color, size]);

  const sourceList = serverResults || results || [];
  if (!sourceList || sourceList.length === 0) return <div>No results</div>;

  return (loadingServer ? <div>Loading...</div> : sourceList.map(r => (
    <ProductCard
      key={(r && r.id && r.id.raw) || r._id || (r && r._source && r._source.url)}
      result={r}
    />
  )));
}
