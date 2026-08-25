import json, os
d = os.path.dirname(os.path.abspath(__file__))
trip = json.load(open(os.path.join(d, "tripData.json"), encoding="utf-8"))
html = open(os.path.join(d, "template_local.html"), encoding="utf-8").read()
for k, v in {
    "{{TRIP_DATA_JSON}}": json.dumps(trip, ensure_ascii=False, indent=2),
    "{{TRIP_TITLE}}": trip.get("title", ""),
    "{{DATE_RANGE}}": trip.get("dateRange", ""),
    "{{TRAVELERS}}": trip.get("travelers", ""),
    "{{TOTAL_BUDGET}}": str(trip.get("budget", {}).get("total", 0)),
    "{{PER_PERSON}}": str(trip.get("budget", {}).get("perPerson", 0)),
    "{{GENERATION_DATE}}": trip.get("generationDate", ""),
}.items():
    html = html.replace(k, v)
out = os.path.join(d, "德国瑞士-14天旅行计划-修订版.html")
open(out, "w", encoding="utf-8").write(html)
print("Generated:", out)
