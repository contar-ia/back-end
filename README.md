# to build: 

```bash
docker build -t my-fastapi-app .
```

# to run:

```bash
sudo docker run -p 8000:8000 \
    -v "$(pwd)":/app \
    my-fastapi-app
```