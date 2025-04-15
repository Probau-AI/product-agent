# Installation

install dependencies with uv
```
uv sync
```

# Usage
run locally with
```
uv run uvicorn main:app --reload
```

or with docker
```
docker build -t scrapy .

docker run -p 8000:8000 scrapy
```

# Example
send request to `/get` endpoint this data
```
{
    "sentence": "Show me the list of green sofas, show cheapest ones first",
}
```

