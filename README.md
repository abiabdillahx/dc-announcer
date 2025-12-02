# Discord Announcer
Simple discord announcer panel with webhook

## How to use it
### Preparation
1. Create discord webhook into your channel
2. Install `docker`

### 1. Clone this repo
```sh
git clone https://github.com/abiabdillahx/dc-announcer
```

### 2. Copy the env example
```sh
cp .env.example .env
```
Edit it with your own token and webhook

### 3. Run it locally
```sh
docker build -t announcement-panel .

docker run -d -p 5000:5000 --env-file .env announcement-panel

```
Then, open [http://localhost:5000](http://localhost:5000)
