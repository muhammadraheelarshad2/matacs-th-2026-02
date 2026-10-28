"""Deterministic scoring step (plain code, no AI).
Input: structured fields produced by the AI extraction step (numbers/booleans only).
Run: python prototype/score.py
"""
import json, pathlib

CRITERIA = {  # would come from the admin database, never hard-coded in production
    "ceiling": 260000, "max_weeks": 16,
    "weights": {"experience": 30, "price": 25, "timeline": 15, "warranty": 15, "team": 15},
}

def score_all(rows, c=CRITERIA):
    w = c["weights"]
    out = {}
    for r in rows:
        o = out[r["proposal"]] = {"status": None, "flags": [], "score": None, "parts": {}}
        if not (r["licence_held_by_bidder"] and r["wsib"] and r["insurance_5m"]):
            o["status"] = "ineligible"; continue
        if r["price_cad"] > c["ceiling"]:
            o["status"] = "ineligible"; continue
        if r["injection_suspected"]: o["flags"].append("manipulation attempt")
        if r["weeks"] is None or r["weeks"] > c["max_weeks"]: o["flags"].append("timeline missing/over 16 weeks")
        o["status"] = "flagged" if o["flags"] else "ranked"

    pool = [r for r in rows if out[r["proposal"]]["status"] != "ineligible"]  # baseline = mandatory-pass set
    best_price = min(r["price_cad"] for r in pool)
    best_weeks = min(r["weeks"] for r in pool if r["weeks"] is not None)
    best_inst = max(r["installs_100kw_5y"] for r in pool)
    best_wm = max(r["workmanship_yrs"] for r in pool)

    for r in pool:
        p = {}
        p["experience"] = w["experience"] * r["installs_100kw_5y"] / best_inst
        p["price"] = w["price"] * best_price / r["price_cad"]
        p["timeline"] = w["timeline"] * best_weeks / r["weeks"] if r["weeks"] else 0.0
        p["warranty"] = w["warranty"] * (0.5 * min(r["panel_warranty_yrs"] / 25, 1) + 0.5 * r["workmanship_yrs"] / best_wm)
        items = [r["named_lead"], r["crew_stated"], r["safety_plan"], r["monitoring_plan"]]
        p["team"] = w["team"] * sum(items) / 4
        o = out[r["proposal"]]
        o["parts"] = {k: round(v, 2) for k, v in p.items()}
        o["merit_score"] = round(sum(p.values()), 1)
        if o["status"] == "ranked": o["score"] = o["merit_score"]
    return out

if __name__ == "__main__":
    rows = json.loads((pathlib.Path(__file__).parent / "sample_extractions.json").read_text())
    res = score_all(rows)
    ranked = sorted([k for k, v in res.items() if v["status"] == "ranked"], key=lambda k: -res[k]["score"])
    for i, k in enumerate(ranked, 1): res[k]["rank"] = i
    print(json.dumps(res, indent=2))
