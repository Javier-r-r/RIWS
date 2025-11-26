import React, { useEffect, useState } from "react";
import "./ProductCard.css";

export default function ProductDetailModal({ product, onClose }) {
  const images = (product && (product.images || product.image)) || [];
  const imgs = Array.isArray(images) ? images : (images ? [images] : []);
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowLeft") setIdx(i => Math.max(0, i - 1));
      if (e.key === "ArrowRight") setIdx(i => Math.min(imgs.length - 1, i + 1));
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [imgs.length, onClose]);

  if (!product) return null;

  const title = product.title || product.name || "No title";
  const description = product.description || product.desc || "";
  const price = product.price != null ? product.price : null;
  const currency = product.currency || "";
  const sizes = product.sizes || product.size || [];
  const sizesArr = Array.isArray(sizes) ? sizes : (sizes ? [sizes] : []);

  return (
    <div className="pdm-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="pdm-panel" onClick={e => e.stopPropagation()}>
        <button className="pdm-close" onClick={onClose} aria-label="Close">×</button>
        <div className="pdm-content">
          <div className="pdm-carousel">
            {imgs.length > 0 ? (
              <>
                <div className="pdm-image-wrap">
                  <img src={imgs[idx]} alt={title} />
                </div>
                <div>
                    <button className="pdm-nav pdm-prev" onClick={() => setIdx(i => Math.max(0, i - 1))} disabled={idx === 0}>‹</button>
                    <button className="pdm-nav pdm-next" onClick={() => setIdx(i => Math.min(imgs.length - 1, i + 1))} disabled={idx === imgs.length - 1}>›</button>
                </div>
                <div className="pdm-controls">
                  <div className="pdm-thumbs">
                    {imgs.map((u, i) => (
                      <img key={u + i} src={u} alt={`${title} ${i+1}`} className={i === idx ? 'active' : ''} onClick={() => setIdx(i)} />
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="pdm-no-image">No images</div>
            )}
          </div>
          <div className="pdm-info">
            <h2>{title}</h2>
            {price !== null ? (
              <div className="pdm-price"><span className="pdm-currency">{currency}</span> <span className="pdm-amount">{Number(price).toFixed(2)}</span></div>
            ) : <div className="pdm-price">N/A</div>}
            {description && <p className="pdm-desc">{description}</p>}
            {sizesArr && sizesArr.length > 0 && (
              <div className="pdm-sizes">
                <div className="pdm-sizes-label">Sizes</div>
                <div className="pdm-sizes-list">{sizesArr.map(s => <span key={s} className="pdm-size">{s}</span>)}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
