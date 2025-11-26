#!/usr/bin/env python3
"""
Safe delete for Elasticsearch index `scuffers_products`.

Usage:
  python index_tools/delete_index.py        # interactive confirmation
  python index_tools/delete_index.py -y     # non-interactive (force)

Reads ES host from ES_HOST env var (default http://localhost:9200).
"""
import os
import sys
from elasticsearch import Elasticsearch

ES_HOST = os.environ.get("ES_HOST", "http://localhost:9200")
INDEX = "scuffers_products"


def delete_index(force: bool = False) -> int:
    es = Elasticsearch(ES_HOST)
    if not es.ping():
        print(f"Elasticsearch no responde en {ES_HOST}. Asegúrate de que está levantado.")
        return 2

    try:
        exists = es.indices.exists(index=INDEX)
    except Exception as e:
        print("Error comprobando existencia del índice:", e)
        return 3

    if not exists:
        print(f"Índice '{INDEX}' no existe.")
        return 0

    if not force:
        confirm = input(f"Vas a borrar el índice '{INDEX}'. ¿Confirmas? [y/N] ")
        if confirm.lower() != "y":
            print("Cancelado por el usuario.")
            return 1

    try:
        es.indices.delete(index=INDEX)
        print(f"Índice '{INDEX}' borrado correctamente.")
        return 0
    except Exception as e:
        print("Error borrando índice:", e)
        return 4


if __name__ == "__main__":
    force_flag = ("-y" in sys.argv) or ("--yes" in sys.argv)
    sys.exit(delete_index(force_flag))
