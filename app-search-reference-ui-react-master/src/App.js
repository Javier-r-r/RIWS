import React, { useState, useEffect, useRef } from "react";

import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

import {
  ErrorBoundary,
  Facet,
  SearchProvider,
  SearchBox,
  Results,
  PagingInfo,
  ResultsPerPage,
  Paging,
  Sorting,
  WithSearch
} from "@elastic/react-search-ui";
import { Layout } from "@elastic/react-search-ui-views";
import "@elastic/react-search-ui-views/lib/styles/styles.css";

import {
  buildAutocompleteQueryConfig,
  buildFacetConfigFromConfig,
  buildSearchOptionsFromConfig,
  buildSortOptionsFromConfig,
  getConfig,
  getFacetFields,
  getTitleField,
  getUrlField,
  getThumbnailField
} from "./config/config-helper";

import ProductCard from "./components/ProductCard";
import colorsList from "./config/colors.json";
import sizesList from "./config/sizes.json";

import "./components/ProductCard.css";
import "./custom-overrides.css";
import RecentSearchBox from "./components/RecentSearchBox";
import ServerSortedResults from "./components/ServerSortedResults";

const connector = new ElasticsearchAPIConnector({
  host: "http://localhost:9200",
  index: "scuffers_products"
});
const config = {
  searchQuery: {
    facets: buildFacetConfigFromConfig(),
    ...buildSearchOptionsFromConfig()
  },
  autocompleteQuery: buildAutocompleteQueryConfig(),
  apiConnector: connector,
  alwaysSearchOnInitialLoad: true
};

export default function App() {
  const [sortMode, setSortMode] = useState(null);
  const [filtersCollapsed, setFiltersCollapsed] = useState(false);
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [selectedColor, setSelectedColor] = useState("");
  const [selectedSize, setSelectedSize] = useState("");

  
  return (
    <SearchProvider config={config}>
      <WithSearch mapContextToProps={({ wasSearched }) => ({ wasSearched })}>
        {({ wasSearched }) => {
          return (
            <div className={"App " + (filtersCollapsed ? 'filters-collapsed' : '')} style={{ position: 'relative' }}>
              <button
                onClick={() => setFiltersCollapsed(c => !c)}
                title={filtersCollapsed ? 'Show filters' : 'Hide filters'}
                aria-label={filtersCollapsed ? 'Show filters' : 'Hide filters'}
                style={{ position: 'absolute', left: 12, top: 120, padding: 6, zIndex: 2000, background: 'white', border: '1px solid #ddd', borderRadius: 4 }}
              >
                {/* simple filter/funnel icon */}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M3 5h18v2L13 13v6l-2 1v-7L3 7V5z" fill="#444" />
                </svg>
              </button>
              <ErrorBoundary>
                <Layout
                  header={
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <div style={{ flex: 1 }}>
                        <RecentSearchBox />
                      </div>
                    </div>
                  }
                  sideContent={
                    filtersCollapsed ? null : (
                      <div>
                          <div>
                          {wasSearched && (
                            <div style={{marginBottom:12}}>
                              <div style={{marginBottom:8}}>
                                <button
                                  onClick={() => setSortMode('price_asc')}
                                  style={{
                                    marginRight: 6,
                                    ...(sortMode === 'price_asc' ? { fontWeight: '600', background: '#f2f6fb', border: '1px solid #cbdff0' } : {})
                                  }}
                                >
                                  Price ↑
                                </button>
                                <button
                                  onClick={() => setSortMode('price_desc')}
                                  style={{
                                    ...(sortMode === 'price_desc' ? { fontWeight: '600', background: '#f2f6fb', border: '1px solid #cbdff0' } : {})
                                  }}
                                >
                                  Price ↓
                                </button>
                                <button onClick={() => setSortMode(null)} style={{marginLeft:8}}>Clear Sort</button>
                              </div>
                              <div style={{display:'flex', flexDirection:'column', gap:8}}>
                                <div style={{display:'flex', gap:8, alignItems:'center'}}>
                                  <input placeholder="min price" type="number" value={minPrice} onChange={e=>setMinPrice(e.target.value)} style={{width:'50%',padding:6}} />
                                  <input placeholder="max price" type="number" value={maxPrice} onChange={e=>setMaxPrice(e.target.value)} style={{width:'50%',padding:6}} />
                                </div>
                                <div>
                                  <div style={{display:'flex', flexDirection:'column', gap:6}}>
                                    <select value={selectedColor} onChange={e=>setSelectedColor(e.target.value)} style={{padding:6, width:'100%'}}>
                                      <option value="">All colors</option>
                                      {colorsList.map(c => (
                                        <option key={c} value={c}>{c}</option>
                                      ))}
                                    </select>
                                    <select value={selectedSize} onChange={e=>setSelectedSize(e.target.value)} style={{padding:6, width:'100%'}}>
                                      <option value="">All sizes</option>
                                      {sizesList.map(s => (
                                        <option key={s} value={s}>{s}</option>
                                      ))}
                                    </select>
                                  </div>
                                </div>
                                <div style={{display:'flex', gap:8}}>
                                  <button onClick={() => { setMinPrice(""); setMaxPrice(""); setSortMode(s=>s); setSelectedColor(""); setSelectedSize(""); }} style={{marginLeft:6}}>Clear Filters</button>
                                </div>
                              </div>
                            </div>
                          )}
                          {getFacetFields().filter(f => f !== 'sizes').map(field => (
                            <Facet key={field} field={field} label={field} />
                          ))}
                        </div>
                      </div>
                    )
                  }
                  bodyContent={
                    <div className="results-grid">
                      <WithSearch mapContextToProps={({ results, searchTerm, current, resultsPerPage }) => ({ results, searchTerm, current, resultsPerPage })}>
                        {(props) => <ServerSortedResults {...props} sortMode={sortMode} minPrice={minPrice} maxPrice={maxPrice} color={selectedColor} size={selectedSize} />}
                      </WithSearch>
                    </div>
                  }
                  bodyHeader={
                    <React.Fragment>
                      {wasSearched && <PagingInfo />}
                      {wasSearched && <ResultsPerPage />}
                    </React.Fragment>
                  }
                  bodyFooter={<Paging />}
                />
              </ErrorBoundary>
            </div>
          );
        }}
      </WithSearch>
    </SearchProvider>
  );
}
