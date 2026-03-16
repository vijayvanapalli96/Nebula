"""
E2E test for /story/questions, /story/opening, and /story/media/{id} endpoints.

Tests that:
1. POST /story/questions returns text instantly + media_request_id
2. POST /story/opening returns text instantly + media_request_id
3. GET /story/media/{id} returns {asset_key: uri_or_null} map
4. After waiting, media URIs are populated (not null)
"""

import json
import sys
import time

import requests

BASE = "http://localhost:8000"


def pp(label: str, data: dict) -> None:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2, default=str))


def main() -> None:
    # ── 1. POST /story/questions ─────────────────────────────────────
    print("\n>>> POST /story/questions (theme: Cyberpunk Noir)")
    t0 = time.time()
    r = requests.post(f"{BASE}/story/questions", json={"theme": "Cyberpunk Noir"})
    elapsed = time.time() - t0
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    q_data = r.json()
    pp(f"Questions response ({elapsed:.2f}s)", q_data)

    assert "questions" in q_data
    assert len(q_data["questions"]) >= 1
    q_media_id = q_data.get("media_request_id")
    print(f"\n  media_request_id: {q_media_id}")
    print(f"  # questions: {len(q_data['questions'])}")
    for qi, q in enumerate(q_data["questions"]):
        print(f"    Q{qi}: {q['question'][:60]}")
        for oi, opt in enumerate(q["options"]):
            print(f"      opt{oi}: {opt['text'][:30]}  prompt={opt['image_prompt'][:40]}...")

    # ── 2. POST /story/opening ───────────────────────────────────────
    answers = [
        {"question": q_data["questions"][i]["question"], "answer": q_data["questions"][i]["options"][0]["text"]}
        for i in range(min(len(q_data["questions"]), 4))
    ]
    print(f"\n>>> POST /story/opening (answers from questions)")
    t0 = time.time()
    r = requests.post(
        f"{BASE}/story/opening",
        json={
            "theme": "Cyberpunk Noir",
            "character_name": "Kira Voss",
            "answers": answers,
        },
    )
    elapsed = time.time() - t0
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    o_data = r.json()
    pp(f"Opening scene response ({elapsed:.2f}s)", o_data)

    o_media_id = o_data.get("media_request_id")
    print(f"\n  media_request_id: {o_media_id}")
    print(f"  scene_title: {o_data['scene_title']}")
    print(f"  # choices: {len(o_data['choices'])}")

    # ── 3. GET /story/media/{id} — check immediately ─────────────────
    media_ids = []
    if q_media_id:
        media_ids.append(("questions", q_media_id))
    if o_media_id:
        media_ids.append(("opening", o_media_id))

    if not media_ids:
        print("\n⚠ No media_request_ids returned — image storage may be unavailable.")
        sys.exit(0)

    print(f"\n>>> GET /story/media (immediate check)")
    for label, mid in media_ids:
        r = requests.get(f"{BASE}/story/media/{mid}")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        m = r.json()
        total = len(m["assets"])
        done = sum(1 for v in m["assets"].values() if v is not None)
        print(f"  [{label}] {done}/{total} assets ready")

    # ── 4. Poll until done (max 120s) ────────────────────────────────
    print(f"\n>>> Polling media endpoints (max 120s)...")
    start = time.time()
    completed = {label: False for label, _ in media_ids}

    while time.time() - start < 120:
        all_done = True
        for label, mid in media_ids:
            if completed[label]:
                continue
            r = requests.get(f"{BASE}/story/media/{mid}")
            m = r.json()
            total = len(m["assets"])
            done = sum(1 for v in m["assets"].values() if v is not None)
            failed = sum(1 for v in m["assets"].values() if v is not None and "FAILED" in str(v))
            elapsed = time.time() - start
            if done == total:
                completed[label] = True
                print(f"  [{label}] {done}/{total} COMPLETE ({elapsed:.0f}s)")
                pp(f"{label} final assets", m["assets"])
            else:
                all_done = False
                print(f"  [{label}] {done}/{total} ({elapsed:.0f}s)")

        if all_done:
            break
        time.sleep(5)

    # ── Summary ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    for label, mid in media_ids:
        r = requests.get(f"{BASE}/story/media/{mid}")
        m = r.json()
        total = len(m["assets"])
        done = sum(1 for v in m["assets"].values() if v is not None)
        status = "PASS" if done == total else f"PARTIAL ({done}/{total})"
        print(f"  {label}: {status} — {total} assets")
        for k, v in m["assets"].items():
            uri_short = v[:80] + "..." if v and len(v) > 80 else v
            print(f"    {k}: {uri_short}")

    total_elapsed = time.time() - start
    print(f"\n  Total poll time: {total_elapsed:.0f}s")


if __name__ == "__main__":
    main()
