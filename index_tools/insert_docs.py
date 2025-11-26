from elasticsearch import Elasticsearch, helpers
import json
from pathlib import Path
from color_utils import infer_color_from_url

ES_HOST = "http://localhost:9200"
INDEX_NAME = "scuffers_products"

es = Elasticsearch(hosts=[ES_HOST])


def parse_price(p):
	if p is None:
		return None
	try:
		s = str(p).strip()
		s = s.replace('€', '').replace('$', '')
		s = s.replace('\u20ac', '')
		if ',' in s and '.' not in s:
			s = s.replace(',', '.')
		s = s.replace(',', '')
		return float(s)
	except Exception:
		return None


def load_json(path: Path):
	with path.open('r', encoding='utf-8') as f:
		return json.load(f)


def docs_from_file(path: Path):
	data = load_json(path)
	for doc in data:
		price = parse_price(doc.get('price'))
		doc['price'] = price
		# infer color from url and normalize to lower-case
		try:
			color = infer_color_from_url(doc.get('url') or '')
		except Exception:
			color = 'unknown'
		doc['color'] = (color or 'unknown').lower()
		for k in ['url', 'title', 'description', 'currency', 'images', 'sku', 'availability', 'sizes', 'size']:
			if k not in doc:
				doc[k] = None
		_id = None
		if doc.get('url'):
			_id = doc.get('url')
		elif doc.get('sku'):
			_id = doc.get('sku')

		action = {
			'_index': INDEX_NAME,
			'_id': _id,
			'_source': doc,
		}
		yield action


def main():
	path = Path(__file__).resolve().parents[1] / 'scuffers_output.json'
	if not path.exists():
		print(f"File not found: {path}")
		return

	actions = docs_from_file(path)
	success, failed = 0, 0
	try:
		resp = helpers.bulk(es, actions, stats_only=True)
		success = resp
		print(f"Indexed {success} documents into '{INDEX_NAME}'.")
	except Exception as e:
		print("Bulk indexing failed:", e)


if __name__ == '__main__':
	main()

