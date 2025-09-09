import requests

STT_URL = "http://localhost:8001/transcribe"

def transcribe_file(path, language=None):
    with open(path, "rb") as f:
        files = {"file": (path, f, "audio/wav")}
        params = {}
        if language:
            params["language"] = language
        r = requests.post(STT_URL, files=files, params=params, timeout=120)
        r.raise_for_status()
        return r.json()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python client_example.py <audio-file>")
        sys.exit(1)
    print(transcribe_file(sys.argv[1]))
