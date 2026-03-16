"""E2E test: verify /story/opening returns image_uri on each choice."""
import json, time, requests

# Step 1: generate questions
print("Generating questions...")
r1 = requests.post("http://localhost:8000/story/questions", json={"theme": "Cyberpunk Noir"})
body1 = r1.json()
print(f"  Questions: {len(body1['questions'])}")

# Build answers from first option of each question
answers = []
for q in body1["questions"]:
    answers.append({"question": q["question"], "answer": q["options"][0]["text"]})

# Step 2: generate opening scene
print("\nGenerating opening scene...")
t0 = time.time()
r2 = requests.post("http://localhost:8000/story/opening", json={
    "theme": "Cyberpunk Noir",
    "character_name": "Kira Voss",
    "answers": answers,
})
elapsed = time.time() - t0
body2 = r2.json()

print(f"Status: {r2.status_code}  Time: {elapsed:.1f}s")
print(f"Scene: {body2.get('scene_title', 'N/A')}")
print(f"Description: {body2.get('scene_description', 'N/A')[:80]}...")
print(f"Choices: {len(body2.get('choices', []))}")
print(f"media_request_id: {body2.get('media_request_id')}")

uris_found = 0
for i, c in enumerate(body2.get("choices", [])):
    uri = c.get("image_uri")
    if uri:
        uris_found += 1
    short = (uri[:70] + "...") if uri and len(uri) > 70 else uri
    print(f"  choice {c['choice_id']}: {c['choice_text'][:30]:30s}  image_uri={short}")

total = len(body2.get("choices", []))
print(f"\n{'='*60}")
print(f"  RESULT: {uris_found}/{total} choices have image_uri")
print(f"  Opening scene response time: {elapsed:.1f}s")
print(f"  Video generation: {'background (media_request_id=' + body2.get('media_request_id', '') + ')' if body2.get('media_request_id') else 'no videos'}")
print(f"{'='*60}")
