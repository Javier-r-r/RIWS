// hooks/useNavigationHistory.js
import { useState, useEffect } from "react";

export default function useNavigationHistory(maxItems = 20) {
  const STORAGE_KEY = "navigationHistory";
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    setHistory(stored);
  }, []);

  const addToHistory = (item) => {
    if (!item) return;
    let updated = [item, ...history.filter(h => h.id !== item.id)];
    if (updated.length > maxItems) updated = updated.slice(0, maxItems);
    setHistory(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return { history, addToHistory, clearHistory };
}
