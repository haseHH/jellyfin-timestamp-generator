# Jellyfin Timestamp Generator

Originally intended for live streamer's watchalongs, might be useful to others as well 🙂

## Usage

Build and start the container with your API key and server address in the environment variables, and access the HTTP endpoint with your browser. A full info page with options and styling parameters will guide you. Build the parameters as you like and matches your setup, then copy the full link into OBS as a browser source. Make sure to remove any custom CSS to prevent flickering.

You can deploy the code yourself or use the provided container image `ghcr.io/hasehh/jellyfin-timestamp-generator:v1.0.0`. Make sure to provide the `JF_ADDRESS` and `JF_API_KEY` environment variables.

## Start interactive Development Environment

This will start a fresh container, install the `requirements.txt` and open a `sh` shell. The source code is mounted into it, so all changes are available immediately. When exiting the container, it will be deleted.

Make sure to replace the values in `<>` and preserve the space before `export`, it should prevent leaving the key in your shell's history. Include the protocol in the address, depending on your setup with or without encryption.

```bash
 export KEY=<YOUR_JELLYFIN_API_KEY>
docker run --rm -it -p 8000:8000 --env JF_ADDRESS=http[s]://<YOUR_JELLYFIN_ADDRESS> --env JF_API_KEY=$KEY \
  -v ./src:/app python:3.14-alpine sh -c "cd /app && pip install -r requirements.txt && fastapi dev main.py --host 0.0.0.0"
```

## Special Thanks

A big thank you to [Niels van Velzen](https://github.com/nielsvanvelzen) and his [API Auth Gist](https://gist.github.com/nielsvanvelzen/ea047d9028f676185832e51ffaf12a6f). While a Jellyfin developer guide is in the works, this document he prepared for it remains the most concise and helpful resource I could find when starting this.
