"""Fetch questions and open the first image in the browser."""
import json
import webbrowser
import requests

r = requests.post("http://localhost:8000/story/questions", json={"theme": "Cyberpunk Noir"})
body = r.json()

# Collect all image URIs
uris = []
for q in body["questions"]:
    for o in q["options"]:
        uri = o.get("image_uri")
        if uri:
            uris.append(uri)

print(f"Found {len(uris)} image URIs")
for i, u in enumerate(uris):
    print(f"  [{i}] {u[:100]}...")

if uris:
    print(f"\nOpening first 4 images (one per question) in browser...")
    # Open the first option from each question
    for idx in [0, 4, 8, 12]:
        if idx < len(uris):
            webbrowser.open(uris[idx])
