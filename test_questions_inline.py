"""Quick test: verify /story/questions returns image_uri in each option."""
import json, time, requests

t0 = time.time()
r = requests.post("http://localhost:8000/story/questions", json={"theme": "Cyberpunk Noir"})
elapsed = time.time() - t0
body = r.json()

print(f"Status: {r.status_code}  Time: {elapsed:.1f}s")
print(f"Theme: {body['theme']}")
print(f"Questions: {len(body['questions'])}")

uris_found = 0
uris_total = 0
for i, q in enumerate(body["questions"]):
    print(f"\n  Q{i}: {q['question'][:60]}")
    for j, o in enumerate(q["options"]):
        uris_total += 1
        uri = o.get("image_uri")
        if uri:
            uris_found += 1
        short = (uri[:70] + "...") if uri and len(uri) > 70 else uri
        print(f"    opt{j}: {o['text'][:30]:30s}  image_uri={short}")

print(f"\n{'='*60}")
print(f"  RESULT: {uris_found}/{uris_total} options have image_uri")
print(f"  Response time: {elapsed:.1f}s (includes image gen)")
print(f"{'='*60}")
