# Maze Quiz Docker

This folder now includes a minimal Docker setup for the CLI maze game.

## Build

```bash
docker build -t <your-dockerhub-username>/maze-quiz:latest .
```

## Run

```bash
docker run -it --rm <your-dockerhub-username>/maze-quiz:latest
```

## Login and Push

```bash
docker login
docker push <your-dockerhub-username>/maze-quiz:latest
```

## Local Test

```bash
python -m unittest discover -s .
```

The container starts `maze_game.py` directly and does not use a virtual environment or pygame.