# to build: 

```bash
docker build -t contaria-server .
```

# to run:

```bash
docker run -p 8000:8000 \
    -v "$(pwd)":/app \
    contaria-server
```