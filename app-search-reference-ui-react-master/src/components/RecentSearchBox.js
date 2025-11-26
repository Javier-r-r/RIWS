import React, { useState, useEffect, useRef } from "react";
import { WithSearch, SearchBox } from "@elastic/react-search-ui";

function RecentSearchInner({ setSearchTerm, search, results, wasSearched, isLoading }) {
  const [recent, setRecent] = useState(() => {
    try { const v = localStorage.getItem('recentSearches'); return v ? JSON.parse(v) : []; } catch (e) { return []; }
  });
  const [show, setShow] = useState(false);
  const wrapperRef = useRef(null);

  const loadRecent = () => {
    try { const v = localStorage.getItem('recentSearches'); return v ? JSON.parse(v) : []; } catch (e) { return []; }
  };

  useEffect(() => {
    if (typeof isLoading !== 'undefined') {
      if (!isLoading && wasSearched) setShow(false);
    } else if (wasSearched) {
      setShow(false);
    }
  }, [wasSearched, isLoading, results]);

  useEffect(() => {
    const wrapper = wrapperRef.current;
    if (!wrapper) return;
    const input = wrapper.querySelector('input');
    const button = wrapper.querySelector('button');

    const saveTerm = () => {
      if (!input) return;
      const val = String(input.value || '').trim();
      if (!val) return;
      const now = loadRecent();
      const filtered = now.filter(x => x !== val);
      filtered.unshift(val);
      const limited = filtered.slice(0, 10);
      try { localStorage.setItem('recentSearches', JSON.stringify(limited)); } catch (e) {}
      setRecent(limited);
    };

    const onKeyDown = (e) => { if (e.key === 'Enter') setTimeout(saveTerm, 0); };
    const onButtonClick = () => setTimeout(saveTerm, 0);
    const onFocus = () => { setRecent(loadRecent()); setShow(true); };
    const onBlur = () => setTimeout(() => setShow(false), 150);

    if (input) {
      input.addEventListener('keydown', onKeyDown);
      input.addEventListener('focus', onFocus);
      input.addEventListener('blur', onBlur);
    }
    if (button) button.addEventListener('click', onButtonClick);

    return () => {
      if (input) {
        input.removeEventListener('keydown', onKeyDown);
        input.removeEventListener('focus', onFocus);
        input.removeEventListener('blur', onBlur);
      }
      if (button) button.removeEventListener('click', onButtonClick);
    };
  }, [wrapperRef.current]);

  const onItemClick = (term) => {
    if (typeof setSearchTerm === 'function') {
      try {
        setSearchTerm(term);
        if (typeof search === 'function') search();
        const now = loadRecent();
        const filtered = now.filter(x => x !== term);
        filtered.unshift(term);
        const limited = filtered.slice(0, 10);
        try { localStorage.setItem('recentSearches', JSON.stringify(limited)); } catch (e) {}
        setRecent(limited);
        return;
      } catch (e) {}
    }

    const wrapper = wrapperRef.current;
    if (!wrapper) return;
    const input = wrapper.querySelector('input');
    if (!input) return;
    input.focus();
    input.value = term;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    const btn = wrapper.querySelector('button');
    if (btn) { btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true })); setTimeout(() => btn.click(), 0); }
    else { input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }
    const now = loadRecent();
    const filtered = now.filter(x => x !== term);
    filtered.unshift(term);
    const limited = filtered.slice(0, 10);
    try { localStorage.setItem('recentSearches', JSON.stringify(limited)); } catch (e) {}
    setRecent(limited);
  };

  return (
    <div ref={wrapperRef} style={{ position: 'relative' }}>
      <SearchBox autocompleteSuggestions={false} />
      {show && recent && recent.length > 0 && (
        <div style={{ position: 'absolute', left: 0, right: 0, top: 'calc(100% + 6px)', background: '#fff', border: '1px solid #ddd', zIndex: 9999, maxHeight: 220, overflow: 'auto' }}>
          {recent.map((r, idx) => (
            <div key={r + String(idx)} style={{ padding: 8, borderBottom: '1px solid #f3f3f3', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div onMouseDown={(e) => { e.preventDefault(); onItemClick(r); }} style={{ flex: 1 }}>{r}</div>
              <button
                onMouseDown={(e) => { e.stopPropagation(); e.preventDefault(); }}
                onClick={() => {
                  try {
                    const stored = localStorage.getItem('recentSearches');
                    const arr = stored ? JSON.parse(stored) : [];
                    const filtered = arr.filter(x => x !== r);
                    localStorage.setItem('recentSearches', JSON.stringify(filtered));
                    setRecent(filtered);
                  } catch (err) {}
                }}
                title="Eliminar"
                style={{ marginLeft: 8, background: 'transparent', border: 'none', cursor: 'pointer', color: '#888', fontSize: 14 }}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function RecentSearchBox() {
  return (
    <WithSearch mapContextToProps={({ setSearchTerm, searchTerm, search, results, wasSearched, isLoading }) => ({ setSearchTerm, searchTerm, search, results, wasSearched, isLoading })}>
      {(ctx) => <RecentSearchInner {...ctx} />}
    </WithSearch>
  );
}
