"""Build data.json from Daily Check-in rows exported from Notion.
Usage: python3 scripts/build_data.py rows.json > data.json
rows.json = [{"d":"YYYY-MM-DD","h":"[\"https://app.notion.com/<id>\", ...]"}, ...]
"""
import json, sys, datetime, re
HABITS = {  # short key -> (notion page id, display name)
    "gym":  ("4015745be48681459b7ec613a9342730", "Gym / run"),
    "wake": ("4015745be4868193ae60c86c0336a9e1", "Wake up early"),
    "pray-am": ("4015745be48681838530e9763b76e99c", "Morning prayer"),
    "pray-pm": ("4015745be486812498d7f95dccf5fbd3", "Evening prayer"),
    "church": ("4015745be48681ffb22cf26fc79c3948", "Church"),
    "read-biz": ("4015745be48681f6b050f3809dd3529f", "Business book"),
    "read-med": ("4015745be48681ca90b7fbb0ac8ea93d", "Meditations"),
}
rows = json.load(open(sys.argv[1]))
counts, habits = {}, {k: {"name": v[1], "days": {}} for k, v in HABITS.items()}
for r in rows:
    d = (r.get("d") or "")[:10]
    if not d: continue
    ids = [re.sub(r".*/", "", u).replace("-", "") for u in json.loads(r.get("h") or "[]")]
    counts[d] = counts.get(d, 0) + len(ids)
    for k, (pid, _) in HABITS.items():
        if pid in ids: habits[k]["days"][d] = 1
print(json.dumps({"updated": datetime.date.today().isoformat(), "counts": counts, "habits": habits}, indent=1))
