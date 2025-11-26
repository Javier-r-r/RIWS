import re
from urllib.parse import urljoin

import scrapy
from bs4 import BeautifulSoup
from scraper.items import ScraperItem


class ScuffersSpider(scrapy.Spider):
    name = 'scuffers'
    allowed_domains = ['scuffers.com']
    start_urls = ['https://scuffers.com/']

    # Conservative crawling settings for this spider
    custom_settings = {
        # Respect robots.txt rules
        'ROBOTSTXT_OBEY': True,
        # Polite user agent identifying the project
        'USER_AGENT': 'RIWS-scuffers-scraper/1.0 (+https://github.com/Javier-r-r)',
        # Usar si te bloquean: 'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        # Stop the crawl after scraping 100 items (user request)
        'CLOSESPIDER_ITEMCOUNT': 100,
    }

    price_re = re.compile(r"(?:\$|€|£)?\s*(\d{1,3}(?:[.,]\d{2})?)")

    def parse(self, response):
        # Use BeautifulSoup for page analysis and product detection
        soup = BeautifulSoup(response.text or '', 'html.parser')

        # Detect product pages using conservative heuristics.
        is_product = False

        # JSON-LD product schema
        for script in soup.find_all('script', type='application/ld+json'):
            txt = script.string or script.get_text() or ''
            if re.search(r'"@type"\s*:\s*"Product"', txt):
                is_product = True
                break

        # Open Graph product type
        og = soup.find('meta', attrs={'property': 'og:type'})
        if og and og.get('content', '').lower() == 'product':
            is_product = True

        # Common Shopify product selectors
        if soup.select('[data-product], form[action*="/cart/add"], .product-form, .product-single'):
            is_product = True

        if is_product:
            # --- EXTRAER LA URL CANÓNICA ---
            canonical = soup.find("link", rel="canonical")
            canonical_url = canonical["href"].strip() if canonical and canonical.get("href") else response.url

            # Normalizar por si la URL es relativa
            canonical_url = urljoin(response.url, canonical_url)

            # --- EVITAR PRODUCTOS DUPLICADOS ---
            if not hasattr(self, "seen_products"):
                self.seen_products = set()

            if canonical_url in self.seen_products:
                return  # ya procesado → evitar duplicado

            self.seen_products.add(canonical_url)

            # Llamar a parse_product con la URL canonizada
            yield from self.parse_product(response)
            return

        # Otherwise, follow internal links but be conservative: only follow links within allowed_domains
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if not href:
                continue
            url = urljoin(response.url, href)
            # keep inside domain
            if self.allowed_domains[0] not in url:
                continue

            # avoid hitting checkout/cart/admin/account/search endpoints per robots.txt
            disallowed_substrings = (
                '/cart', '/carts', '/checkout', '/checkouts', '/orders', '/admin', '/account', '/search', '/policies', '/recommendations/products', '/sf_private_access_tokens'
            )
            if any(s in url for s in disallowed_substrings):
                continue

            yield response.follow(url, callback=self.parse)

    def parse_product(self, response):
        # Build item dictionary
        item = {}
        item['url'] = response.url
        text = response.text
        soup = BeautifulSoup(text or '', 'html.parser')

        # Title
        title = ''
        h1 = soup.find('h1')
        if h1 and h1.get_text(strip=True):
            title = h1.get_text(strip=True)
        else:
            ttag = soup.find('title')
            title = ttag.get_text(strip=True) if ttag else ''
        item['title'] = title.strip() if title else ''

        # Description
        description = ''
        paragraph = response.css('div.metafield-rich_text_field')
        description = paragraph.css('p::text').get()

        item['description'] = description.strip() if description else ''

        # Price
        price = ''
        ld = None
        ld_tag = soup.find('script', type='application/ld+json')
        if ld_tag:
            ld = ld_tag.string or ld_tag.get_text()
        if ld:
            m = re.search(r'"price"\s*:\s*"?([\d.,]+)"?', ld)
            if m:
                price = m.group(1)

        if not price:
            # visible price selectors
            sel = []
            for sel_text in soup.select('.price, .product__price, .product-price'):
                txt = sel_text.get_text() or ''
                m = re.search(r'[\d.,]+', txt)
                if m:
                    price = m.group(0)
                    break

        if not price:
            for m in self.price_re.finditer(text):
                price = m.group(1)
                break

        # Currency: JSON-LD priceCurrency first, fallback to visible price text
        currency = ''
        if ld:
            mcur = re.search(r'"priceCurrency"\s*:\s*"([A-Z]{3}|[^\"]+)"', ld)
            if mcur:
                currency = mcur.group(1)

        if not currency:
            price_text = response.css('.price::text, .product__price::text, .product-price::text').get() or ''
            if '€' in price_text:
                currency = 'EUR'
            elif '$' in price_text:
                currency = 'USD'
            elif '£' in price_text:
                currency = 'GBP'
            else:
                mcode = re.search(r'\b([A-Z]{3})\b', price_text)
                if mcode:
                    currency = mcode.group(1)

        item['price'] = price.strip() if price else ''
        item['currency'] = currency

        # Images
        product_imgs = []

        for div in response.css('div.product-media'):
            image = div.css('img.rimage__image')
            product_imgs.append('https:' + image.attrib['src'])

        item['images'] = product_imgs

        # SKU
        sku = ''
        ds = soup.select_one('[data-sku]')
        if ds and ds.get('data-sku'):
            sku = ds.get('data-sku')
        else:
            selt = soup.select_one('.sku') or soup.select_one('.product-sku')
            if selt and selt.get_text(strip=True):
                sku = selt.get_text(strip=True)
        if not sku and ld:
            m = re.search(r'"sku"\s*:\s*"([^\"]+)"', ld)
            if m:
                sku = m.group(1)
        item['sku'] = sku.strip() if sku else ''

        # Availability
        availability = ''
        if ld:
            m = re.search(r'"availability"\s*:\s*"[^\"]*\/([^"}]+)"', ld)
            if m:
                availability = m.group(1)
        if not availability:
            if soup.select('.sold-out, .out-of-stock'):
                availability = 'out_of_stock'
            else:
                availability = 'in_stock'
        item['availability'] = availability
        # First check for regional sizes: if the site provides a size widget
        # we extract those and skip the heavier extraction logic.
        regional_sizes = []
        try:
            wrapper = soup.select_one('div.selector-wrapper[data-option-name="size"]')
            if wrapper:
                for opt in wrapper.select('.size-region-option'):
                    entry = {}
                    for attr, val in opt.attrs.items():
                        if attr.startswith('data-'):
                            key = attr[5:]
                            if key in ('variant-id', 'variant_id', 'id'):
                                continue
                            entry[key] = val
                    if entry:
                        regional_sizes.append(entry)
        except Exception:
            regional_sizes = []

        # regional_sizes extracted above; do not persist this field in the final item
        if regional_sizes:
            # fast path: if regional sizes exist, save them into sizes
            item['sizes'] = regional_sizes
            # set item['size'] from the regional size's label if available
            first_label = ''
            try:
                if isinstance(regional_sizes, list) and regional_sizes:
                    first = regional_sizes[0]
                    if isinstance(first, dict):
                        # prefer 'label', fallback to other common keys
                        first_label = first.get('label') or first.get('size') or first.get('name') or ''
                    else:
                        first_label = str(first)
                if first_label:
                    first_label = str(first_label).strip()
            except Exception:
                first_label = ''
            item['size'] = first_label or ''
        else:
            precomputed_sizes = []

            for sel in soup.select('select[name*="size"] option, select[id*="size"] option, select[class*="size"] option'):
                opt = sel.get_text()
                if opt:
                    val = opt.strip()
                    if val and val.lower() not in ('choose an option', 'select a size', 'select'):
                        precomputed_sizes.append(val)

            for a in soup.select('[data-size], [data-value]'):
                v = a.get('data-size') or a.get('data-value')
                if v:
                    precomputed_sizes.append(v.strip())

            seen_pre = set()
            final_pre = []
            for s in precomputed_sizes:
                if not s:
                    continue
                s_norm = ' '.join(str(s).split())
                if s_norm in seen_pre:
                    continue
                seen_pre.add(s_norm)
                final_pre.append(s_norm)

            item['sizes'] = final_pre
            item['size'] = final_pre[0] if final_pre else ''

        # convert to ScraperItem and yield
        scraped = ScraperItem()
        for k, v in item.items():
            scraped[k] = v

        yield scraped
