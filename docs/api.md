# API Reference

## Table of Contents
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Comics](#comics)
  - [Series](#series)
  - [Publishers](#publishers)
  - [Collections](#collections)
  - [Search](#search)
- [Pagination](#pagination)
- [Filtering](#filtering)
- [Sorting](#sorting)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Webhooks](#webhooks)
- [Examples](#examples)

## Authentication

All API requests require an API key. Include it in the `X-API-Key` header.

```http
GET /api/comics
X-API-Key: your_api_key_here
```

## Base URL

All API endpoints are relative to the base URL:

```
https://api.comicdb.app/v1
```

## Endpoints

### Comics

#### Get All Comics

```http
GET /comics
```

**Query Parameters:**
- `limit`: Number of results per page (default: 20)
- `offset`: Number of results to skip (default: 0)
- `sort`: Field to sort by (default: `-added_date`)
- `include`: Comma-separated list of related resources to include

**Example Response:**
```json
{
  "data": [
    {
      "id": "comic_123",
      "title": "Amazing Spider-Man",
      "issue_number": 1,
      "cover_url": "https://...",
      "added_date": "2023-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0
  }
}
```

#### Get Comic by ID

```http
GET /comics/{id}
```

### Series

#### Get All Series

```http
GET /series
```

### Publishers

#### Get All Publishers

```http
GET /publishers
```

### Collections

#### Get All Collections

```http
GET /collections
```

### Search

#### Search Comics

```http
GET /search
```

**Query Parameters:**
- `q`: Search query
- `field`: Field to search in (title, publisher, etc.)
- `exact`: Whether to perform an exact match (true/false)

## Pagination

All list endpoints support pagination using `limit` and `offset` parameters.

## Filtering

Filter results using query parameters:

```
GET /comics?publisher=Marvel&year=2023
```

## Sorting

Sort results using the `sort` parameter:

```
GET /comics?sort=-issue_number  # Descending
GET /comics?sort=title          # Ascending
```

## Error Handling

Errors are returned with appropriate HTTP status codes and a JSON response:

```json
{
  "error": {
    "code": "not_found",
    "message": "The requested resource was not found.",
    "details": {
      "resource": "comic",
      "id": "123"
    }
  }
}
```

## Rate Limiting

- 100 requests per minute per API key
- 1,000 requests per day per IP address

## Webhooks

Subscribe to events:

- `comic.added`
- `comic.updated`
- `comic.deleted`

## Examples

### Python

```python
import requests

url = "https://api.comicdb.app/v1/comics"
headers = {
    "X-API-Key": "your_api_key_here"
}

response = requests.get(url, headers=headers)
data = response.json()
print(data)
```

### JavaScript

```javascript
const fetch = require('node-fetch');

const url = 'https://api.comicdb.app/v1/comics';
const options = {
  headers: {
    'X-API-Key': 'your_api_key_here'
  }
};

fetch(url, options)
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL

```bash
curl -X GET \
  https://api.comicdb.app/v1/comics \
  -H 'X-API-Key: your_api_key_here'
```
