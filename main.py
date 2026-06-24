from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Tune In API is running 🎵"}


@app.get("/search")
def search(q: str):
    url = f"https://itunes.apple.com/search?term={q}&media=music&limit=20"
    res = requests.get(url)
    data = res.json()
    results = []
    for track in data.get("results", []):
        results.append({
            "id": track.get("trackId"),
            "title": track.get("trackName"),
            "artist": track.get("artistName"),
            "album": track.get("collectionName"),
            "artwork": track.get("artworkUrl100", "").replace("100x100", "600x600"),
            "duration": track.get("trackTimeMillis", 0) // 1000,
            "preview": track.get("previewUrl"),
        })
    return {"results": results}


@app.get("/stream")
def stream(title: str, artist: str):
    url = f"https://itunes.apple.com/search?term={title} {artist}&media=music&limit=1"
    res = requests.get(url)
    data = res.json()
    results = data.get("results", [])
    if not results:
        raise HTTPException(status_code=404, detail="Song not found")
    preview = results[0].get("previewUrl")
    if not preview:
        raise HTTPException(status_code=404, detail="No preview available")
    return {"url": preview, "title": results[0].get("trackName")}


@app.get("/lyrics")
def lyrics(title: str, artist: str):
    try:
        search_url = f"https://api.lyrics.ovh/suggest/{title} {artist}"
        res = requests.get(search_url)
        data = res.json()
        if not data.get("data"):
            return {"lyrics": "Lyrics not found."}
        top = data["data"][0]
        artist_name = top["artist"]["name"]
        track_title = top["title"]
        lyric_url = f"https://api.lyrics.ovh/v1/{artist_name}/{track_title}"
        lyric_res = requests.get(lyric_url)
        lyric_data = lyric_res.json()
        return {"lyrics": lyric_data.get("lyrics", "Lyrics not found.")}
    except:
        return {"lyrics": "Lyrics not found."}