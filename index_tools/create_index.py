from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=["http://localhost:9200"])

index_name = "scuffers_products"

# Recommended settings + mappings: title with keyword and autocomplete subfield, price as float, sizes as keyword
mapping = {
    "settings": {
        "analysis": {
            "filter": {
                "edge_ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 20
                }
            },
            "analyzer": {
                "edge_ngram_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "edge_ngram_filter"]
                },
                "lowercase_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "url": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "lowercase_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "autocomplete": {
                        "type": "text",
                        "analyzer": "edge_ngram_analyzer",
                        "search_analyzer": "lowercase_analyzer"
                    }
                }
            },
            "description": {"type": "text", "analyzer": "lowercase_analyzer"},
            "price": {"type": "float"},
            "currency": {"type": "keyword"},
            "images": {"type": "keyword"},
            "sku": {"type": "keyword"},
            "availability": {"type": "keyword"},
            "sizes": {"type": "keyword"},
            "size": {"type": "keyword"}
                    ,
                    "color": {"type": "keyword"}
        }
    }
}

# Create index (will raise if index exists)
if es.indices.exists(index=index_name):
    print(f"Index '{index_name}' already exists. Skipping creation.")
else:
    es.indices.create(index=index_name, body=mapping)
    print(f"Index '{index_name}' created with mapping.")