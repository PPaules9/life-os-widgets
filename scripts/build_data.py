"""Build data.json for the Life OS widgets from Notion exports.
Usage: python3 scripts/build_data.py checkins.json [milestones.json projects.json todos.json] > data.json
checkins:   [{"d":"YYYY-MM-DD","h":"[\"https://app.notion.com/<id>\",...]"}]
milestones: [{"m":name,"s":status,"p":"[\"<project url>\"]","due":"YYYY-MM-DD"}]
projects:   [{"url":..., "n":name, "s":status, "a":"[\"<area url>\"]"}]
todos:      [{"n":name,"s":status,"d":"__YES__|__NO__","due":"YYYY-MM-DD"}]
"""
import json, sys, datetime, re
HABITS = {
    "gym":  ("4015745be48681459b7ec613a9342730", "Gym / run"),
    "wake": ("4015745be4868193ae60c86c0336a9e1", "Wake up early"),
    "pray-am": ("4015745be48681838530e9763b76e99c", "Morning prayer"),
    "pray-pm": ("4015745be486812498d7f95dccf5fbd3", "Evening prayer"),
    "church": ("4015745be48681ffb22cf26fc79c3948", "Church"),
    "read-biz": ("4015745be48681f6b050f3809dd3529f", "Business book"),
    "read-med": ("4015745be48681ca90b7fbb0ac8ea93d", "Meditations"),
}
AREAS = {
    "ded5745be4868396a0d501e2019c560c": "God",
    "4465745be48682e8ab5d016f88d87b09": "Entrepreneur",
    "c625745be486837dbc6381992cc42bcb": "Athlete",
    "5385745be48683ef81898158ccbd0ea6": "Husband",
    "bcd5745be486822f84e081ab2a11549e": "Salesman",
    "45e5745be48683a8885881d01bb000d4": "Character",
}
pid = lambda u: re.sub(r".*/", "", u).replace("-", "")
load = lambda i: json.load(open(sys.argv[i])) if len(sys.argv) > i else []
rows, ms, ps, ts = load(1), load(2), load(3), load(4)

counts, habits = {}, {k: {"name": v[1], "days": {}} for k, v in HABITS.items()}
for r in rows:
    d = (r.get("d") or "")[:10]
    if not d: continue
    ids = [pid(u) for u in json.loads(r.get("h") or "[]")]
    counts[d] = counts.get(d, 0) + len(ids)
    for k, (h, _) in HABITS.items():
        if h in ids: habits[k]["days"][d] = 1

proj = {}
for p in ps:
    areas = [AREAS.get(pid(u), "") for u in json.loads(p.get("a") or "[]")]
    proj[pid(p["url"])] = {"name": p["n"], "status": p["s"], "area": areas[0] if areas else "", "done": 0, "total": 0, "next": None}
for m in ms:
    for u in json.loads(m.get("p") or "[]"):
        k = pid(u)
        if k not in proj: continue
        proj[k]["total"] += 1
        if m["s"] == "Done": proj[k]["done"] += 1
        elif m.get("due") and (proj[k]["next"] is None or m["due"] < proj[k]["next"]): proj[k]["next"] = m["due"]

todos = [{"done": t.get("d") == "__YES__", "due": (t.get("due") or "")[:10]} for t in ts if t.get("due")]

print(json.dumps({"updated": datetime.date.today().isoformat(), "counts": counts, "habits": habits,
                  "projects": list(proj.values()), "todos": todos}, indent=1))
