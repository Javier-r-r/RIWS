import React, { useState, useEffect } from "react";
import "./ProductCard.css";
import ProductDetailModal from "./ProductDetailModal";

export default function ProductCard({ result }) {
  function getVal(key) {
    if (result && result._source && result._source[key] !== undefined) return result._source[key];
    if (result && result.raw && result.raw[key] !== undefined) return result.raw[key];
    if (result && result.fields && result.fields[key] !== undefined) {
      const v = result.fields[key];
      if (Array.isArray(v)) {
        if (v.length > 0 && v[0] && v[0].raw !== undefined) {
          const raws = v.map(x => (x && x.raw !== undefined ? x.raw : x));
          return raws.length === 1 ? raws[0] : raws;
        }
        return v;
      }
      if (v && v.raw !== undefined) return v.raw;
      return v;
    }
    if (result && result._raw && result._raw[key] !== undefined) return result._raw[key];
    return undefined;
  }

  const title = getVal('title') || getVal('name') || 'No title';
  const price = getVal('price') != null ? getVal('price') : null;
  const currency = getVal('currency') || '';
  const images = getVal('images') || getVal('image') || [];
  let img = null;
  if (Array.isArray(images) && images.length > 0) img = images[0];
  else if (typeof images === 'string' && images.length > 0) img = images;
  const color = getVal('color') || '';

  
  const [remoteSrc, setRemoteSrc] = useState(null);
  const [showDetail, setShowDetail] = useState(false);

  useEffect(() => {
    if ((title === 'No title' || !img) && !remoteSrc) {
      const idVal = (result && result.id && result.id.raw) || result && result._id || (result && result._source && result._source.url);
      if (!idVal) return;
      try {
        const encoded = encodeURIComponent(idVal);
        const index = 'scuffers_products';
        const url = `http://localhost:9200/${index}/_doc/${encoded}`;
        fetch(url)
          .then(r => r.ok ? r.json() : null)
          .then(data => {
            if (data && data._source) setRemoteSrc(data._source);
          })
          .catch(() => {});
      } catch (e) {}
    }
  }, [result, title, img, remoteSrc]);

  const srcOverride = remoteSrc || null;
  const finalTitle = srcOverride ? (srcOverride.title || srcOverride.name) : title;
  const finalPrice = srcOverride && srcOverride.price != null ? srcOverride.price : price;
  const finalCurrency = srcOverride && srcOverride.currency ? srcOverride.currency : currency;
  const finalImages = srcOverride && srcOverride.images ? srcOverride.images : images;
  let finalImg = null;
  if (Array.isArray(finalImages) && finalImages.length > 0) finalImg = finalImages[0];
  else if (typeof finalImages === 'string' && finalImages.length > 0) finalImg = finalImages;

  return (
    <>
    <div className="product-card" onClick={() => setShowDetail(true)} style={{cursor:'pointer'}}>
      <div className="product-image">
        {finalImg ? (
          <img src={finalImg} alt={finalTitle} />
        ) : (
          <div className="product-image-placeholder">No image</div>
        )}
      </div>
      <div className="product-body">
        <h3 className="product-title">{finalTitle}</h3>
        <div className="product-meta">
          {finalPrice !== null ? (
            <div className="product-price">
              <span className="product-currency">{finalCurrency}</span>
              <span className="product-price-amount">{Number(finalPrice).toFixed(2)}</span>
            </div>
          ) : (
            <div className="product-price">N/A</div>
          )}
          {color && <div className="product-color">{color}</div>}
        </div>
        
      </div>
    </div>
    {showDetail && (
      <ProductDetailModal product={(remoteSrc || result._source || result.raw || result._raw)} onClose={() => setShowDetail(false)} />
    )}
    </>
  );
}
