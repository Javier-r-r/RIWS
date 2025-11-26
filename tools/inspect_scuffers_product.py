import requests
from parsel import Selector
import json
import re
import urllib.parse
from pathlib import Path

url = 'https://scuffers.com/es/products/country-burgundy-duffle-bag'
print(f"🔍 Analizando producto: {url}\n")

r = requests.get(url, timeout=30)
sel = Selector(r.text)

fields = {
    "url": url,
    "html_fields": {},
    "json_endpoint": None,
    "json_fields": [],
    "json_example": {}
}

# ---- 1️⃣ JSON-LD ----
ld = sel.xpath('//script[@type="application/ld+json"]/text()').get()
if ld:
    try:
        parsed = json.loads(ld)
        if isinstance(parsed, list):
            parsed = parsed[0]
        if isinstance(parsed, dict) and parsed.get('@type') == 'Product':
            fields["html_fields"]["json_ld"] = list(parsed.keys())
    except Exception:
        pass

# ---- 2️⃣ HTML CAMPOS COMUNES ----
html_candidates = {
    "title": "h1::text",
    "meta_description": 'meta[name=\"description\"]::attr(content)',
    "price": ".price::text, .product__price::text, .product-price::text",
    "sku": "[data-sku]::attr(data-sku), .sku::text, .product-sku::text",
    "variants": "select[name*=\"size\"] option::text, [data-size]::attr(data-size)",
    "image_urls": "img::attr(src), img::attr(data-src)"
}

for name, selector in html_candidates.items():
    value = sel.css(selector).get()
    if value:
        fields["html_fields"][name] = {"selector": selector, "example": value.strip()}

# ---- 3️⃣ JSON ENDPOINTS POSIBLES ----
p = urllib.parse.urlparse(url)
handle = p.path.strip('/').split('/')[-1]
candidates = [
    f'https://{p.hostname}/products/{handle}.json',
    f'https://{p.hostname}/es/products/{handle}.json'
]

def extract_json_keys_and_values(data, prefix='', depth=0, max_depth=3):
    """
    Recursivamente obtiene las claves y ejemplos de valores de un JSON.
    Limita la profundidad para no generar estructuras enormes.
    """
    items = {}
    if isinstance(data, dict) and depth < max_depth:
        for k, v in data.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                items.update(extract_json_keys_and_values(v, new_prefix, depth+1, max_depth))
            else:
                if v not in (None, '', []):
                    items[new_prefix] = v
    elif isinstance(data, list) and len(data) > 0 and depth < max_depth:
        items.update(extract_json_keys_and_values(data[0], prefix + "[0]", depth+1, max_depth))
    return items

for c in candidates:
    try:
        rr = requests.get(c, timeout=10)
        if rr.status_code == 200 and rr.headers.get("Content-Type", "").startswith("application/json"):
            fields["json_endpoint"] = c
            j = rr.json()
            fields["json_fields"] = sorted(extract_json_keys_and_values(j).keys())
            fields["json_example"] = extract_json_keys_and_values(j)
            break
    except Exception as e:
        continue

# ---- 4️⃣ GUARDAR RESULTADO ----
output_path = Path("output_analysis.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(fields, f, ensure_ascii=False, indent=2)

print("✅ Análisis completado.")
print(f"📁 Resultado guardado en: {output_path.resolve()}")
