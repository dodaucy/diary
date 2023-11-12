# Diary

A simple diary for the web.

## ⚠️ Work in progress ⚠️

This project is still in development. You can use it, but the frontend sucks. Furthermore, the backend will get a few changes in the future. If you are interested in the current state, you can look at the [development branch](https://github.com/dodaucy/diary/tree/develop).

## Setup

> [!IMPORTANT]
> It is recommended to put the project behind a reverse proxy, such as [NGINX](https://www.nginx.com/). You should also set the `Host`, `X-Forwarded-For` and `X-Forwarded-Proto` headers. Otherwise, the rate limit will not work properly.

Here is an example NGINX configuration:

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Compose (recommended)

If you set up the project with Docker Compose, you don't need to set up your own database. The database is automatically set up with Docker Compose.

1. Download [docker-compose.yml](https://raw.githubusercontent.com/dodaucy/diary/master/docker-compose.yml)

    ```bash
    curl -fsSL https://raw.githubusercontent.com/dodaucy/diary/master/docker-compose.yml -o docker-compose.yml
    ```

2. Configure

    Create a `.env` file in the same directory as the `docker-compose.yml` file. See [example.env](/example.env) for an example configuration.

3. Run

    ```bash
    docker compose up -d
    ```

    > [!NOTE]
    > Run `docker compose down && curl -fsSL https://raw.githubusercontent.com/dodaucy/diary/master/docker-compose.yml -o docker-compose.yml && docker compose pull && docker compose build && docker compose up -d` to update the containers.

### Docker

1. Clone and build

    ```bash
    git clone https://github.com/dodaucy/diary.git

    cd diary

    docker build -t diary .
    ```

2. Configure

    Create a `.env` file in the diary directory. See [example.env](/example.env) for an example configuration.

3. Run

    Replace `YOUR_ENDPOINT` with the endpoint you want to use. For example 127.0.0.1:8080 or 0.0.0.0:80.

    ```bash
    docker run -d -p YOUR_ENDPOINT:8000 --env-file ./env --restart always --name diary diary
    ```

    > [!NOTE]
    > Run `git pull && docker build -t diary . && docker stop diary && docker rm diary` to update the container. After that, run the command above again.

### Manual

1. Install dependencies

    ```bash
    sudo apt update

    sudo apt install python3 python3-pip python3-venv git -y
    ```

2. Clone and install pip dependencies

    ```bash
    git clone https://github.com/dodaucy/diary.git

    cd diary

    python3 -m venv venv

    source venv/bin/activate

    python3 -m pip install -r requirements.txt

    deactivate
    ```

3. Configure

    Create a `.env` file in the diary directory. See [example.env](/example.env) for an example configuration.

4. Run

    Replace `YOUR_HOSTNAME` and `YOUR_PORT` with the hostname and port you want to use. For example 127.0.0.1 and 8080 or 0.0.0.0 and 80. If the diary is behind a reverse proxy (which is recommended), you should append `--proxy-headers --forwarded-allow-ips *` to the command. Otherwise, the rate limit will not work properly.

    ```bash
    source venv/bin/activate && python3 -m uvicorn src.main:app --host YOUR_HOSTNAME --port YOUR_PORT ; deactivate
    ```

    > [!NOTE]
    > Run `git pull && source venv/bin/activate && python3 -m pip install -Ur requirements.txt ; deactivate` to update the diary. After that, run the command above again.

## License

This project is licensed under the MIT License. See [LICENSE](/LICENSE) for more information.

Copyright (C) 2022 - 2023 dodaucy
