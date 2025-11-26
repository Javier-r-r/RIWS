### RIWS

# Guía de Instalación y Ejecución

Instrucciones para ejecutar el scraper, levantar ElasticSearch, la API y la interfaz de usuario.

## Requisitos Previos

* **Python** instalado.
* **Docker** instalado y en ejecución.
* **Node.js** (para la UI).
* Se recomienda encarecidamente el uso de un entorno virtual (`venv`).

---

## Pasos de Ejecución

### 1. Crear y activar entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
# En Windows: .venv\Scripts\activate
````

### 2\. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3\. Ejecutar el scraper

Puedes modificar el parámetro `CLOSESPIDER_ITEMCOUNT` para ajustar el número de items a procesar.

```bash
python -m scrapy crawl scuffers -O scuffers_output.json -s CLOSESPIDER_ITEMCOUNT=500
```

### 4\. Levantar ElasticSearch con Docker

```bash
docker compose down --remove-orphans
docker compose build
docker compose up -d elasticsearch
```

### 5\. Crear el índice

> **⚠️ Importante:** Esperar unos 20 segundos después de haber levantado el contenedor de Docker en el paso anterior. Si se ejecuta demasiado rápido, el comando puede fallar al no estar ElasticSearch listo.

```bash
python index_tools/create_index.py
```
#### 5.1\. Para borrar el índice si es necesario.

```bash
python index_tools/delete_index.py
```

### 6\. Insertar los documentos

```bash
python index_tools/insert_docs.py 
```

### 7\. Levantar el API

```bash
cd api 
uvicorn main:app --reload --port 8000
```

### 8\. Realizar consultas de prueba (opcional)

Puedes probar que el API responde correctamente con el siguiente comando:

```bash
curl -X 'GET' \
  'http://localhost:8000/search?q=pants&page=1&per_page=20' \
  -H 'accept: application/json'
```

### 9\. Verificación (opcional)

Comprueba el cuerpo de la respuesta (response body). El campo `es` debe encontrarse en `true`.
Esto certifica que se está utilizando **ElasticSearch** para realizar la búsqueda.

### 10\. Ejecutar App-Search (UI)

### Requisitos UI

  * **Node.js** (La referencia usa `v16.13.0`).
      * Puedes usar `nvm` (macOS/Linux) o `nvm-windows`.
      * O descargar desde [nodejs.org](https://nodejs.org/).
  * **npm** (incluido en Node) o **yarn**.

### Instalación y Arranque

Desde la raíz del proyecto:

#### En macOS / Linux (ejemplo con nvm)

```bash
nvm install 16.13.0
nvm use 16.13.0
cd app-search-reference-ui-react-master
npm install
npm start
```

#### En PowerShell / CMD (Windows)

```bash
cd app-search-reference-ui-react-master
npm install
npm start
```

Por defecto, la aplicación se abrirá automáticamente en [http://localhost:3000](http://localhost:3000).
