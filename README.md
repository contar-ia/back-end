# to build: 

```bash
docker build -t conversai-server .
```

# to run:

```bash
sudo docker run -p 8000:8000 \
    -v "$(pwd)":/app \
    conversai-server
```