#!/usr/bin/env python3
"""Fetch daily weather (Open-Meteo + met.no cross-check), wind, pollen and air quality
for each itinerary day and write weather_live.json. Run by GitHub Actions daily.

Data sources (all free, no API key):
  - Open-Meteo forecast (ECMWF/ICON blended): temperature, weather_code, precip prob, wind/gusts
  - Open-Meteo Air Quality (CAMS Europe): PM2.5, European AQI, birch/grass/mugwort/ragweed pollen
  - met.no (Norwegian Meteorological Institute): temperature cross-check

Output shape per date (YYYY-MM-DD):
  { hi, lo, code, rain, wind, gust, aqi, pm25, pollen: {birch, grass, mugwort, ragweed}, sources: {openMeteo, metNo} }
"""
import json, ssl, statistics, sys, time, urllib.request
from collections import defaultdict

BASE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
TZ = 'Europe%2FZurich'
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'germany-trip-planning/1.0 (contact: zhihao@example.com)'}

# destination coords per trip date (mirrors tripData.json weatherLoc)
LOCS = {
    "09/24": ("北京", 39.904, 116.407), "09/25": ("慕尼黑", 48.137, 11.576),
    "09/26": ("慕尼黑", 48.137, 11.576), "09/27": ("福森", 47.568, 10.699),
    "09/28": ("苏黎世", 47.374, 8.541), "09/29": ("琉森", 47.052, 8.306),
    "09/30": ("少女峰", 46.547, 7.985), "10/01": ("伯尔尼", 46.948, 7.452),
    "10/02": ("滴滴湖", 47.917, 8.174), "10/03": ("维尔茨堡", 49.794, 9.929),
    "10/04": ("海德堡", 49.409, 8.695), "10/05": ("巴哈拉赫", 50.060, 7.768),
    "10/06": ("法兰克福", 50.110, 8.682), "10/07": ("法兰克福", 50.110, 8.682),
    "10/08": ("北京", 39.904, 116.407),
}
TRIP_START = "2026-09-24"
TRIP_END = "2026-10-08"


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=timeout, context=CTX))


def openmeteo_forecast(lat, lon):
    u = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
         f"&daily=weather_code,temperature_2m_max,temperature_2m_min,"
         f"precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max"
         f"&timezone={TZ}&forecast_days=16")
    d = get(u)["daily"]
    out = {}
    for i, t in enumerate(d["time"]):
        out[t] = {
            "code": d["weather_code"][i],
            "hi": d["temperature_2m_max"][i],
            "lo": d["temperature_2m_min"][i],
            "rain": d["precipitation_probability_max"][i],
            "wind": d["wind_speed_10m_max"][i],
            "gust": d["wind_gusts_10m_max"][i],
        }
    return out


def metno_crosscheck(lat, lon):
    u = (f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}")
    d = get(u)
    agg = defaultdict(list)
    for t in d["properties"]["timeseries"]:
        inst = t["data"]["instant"]["details"]
        agg[t["time"][:10]].append(inst["air_temperature"])
    out = {}
    for day, temps in agg.items():
        out[day] = {"hi": max(temps), "lo": min(temps)}
    return out


def openmeteo_airquality(lat, lon):
    u = (f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
         f"&hourly=pm2_5,european_aqi,birch_pollen,grass_pollen,mugwort_pollen,ragweed_pollen"
         f"&timezone={TZ}&forecast_days=4&domains=cams_europe")
    d = get(u)
    if "hourly" not in d:
        return {}
    h = d["hourly"]
    agg = defaultdict(lambda: defaultdict(list))
    for i, t in enumerate(h["time"]):
        day = t[:10]
        for k in ("pm2_5", "european_aqi", "birch_pollen", "grass_pollen", "mugwort_pollen", "ragweed_pollen"):
            v = h[k][i]
            if v is not None:
                agg[day][k].append(v)
    out = {}
    for day, vals in agg.items():
        out[day] = {
            "aqi": round(max(vals["european_aqi"])) if vals.get("european_aqi") else None,
            "pm25": round(statistics.mean(vals["pm2_5"])) if vals.get("pm2_5") else None,
            "pollen": {
                "birch": round(max(vals["birch_pollen"])) if vals.get("birch_pollen") else 0,
                "grass": round(max(vals["grass_pollen"])) if vals.get("grass_pollen") else 0,
                "mugwort": round(max(vals["mugwort_pollen"])) if vals.get("mugwort_pollen") else 0,
                "ragweed": round(max(vals["ragweed_pollen"])) if vals.get("ragweed_pollen") else 0,
            },
        }
    return out


def openmeteo_hourly(lat, lon):
    u = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
         f"&hourly=temperature_2m,precipitation_probability,weather_code"
         f"&timezone={TZ}&forecast_days=16")
    d = get(u)["hourly"]
    out = defaultdict(list)
    for i, t in enumerate(d["time"]):
        out[t[:10]].append({
            "h": int(t[11:13]),
            "t": round(d["temperature_2m"][i]) if d["temperature_2m"][i] is not None else None,
            "p": d["precipitation_probability"][i],
            "c": d["weather_code"][i],
        })
    return {k: v for k, v in out.items()}


def pollen_level(grains):
    if grains is None or grains <= 0:
        return 0
    if grains <= 10:
        return 1
    if grains <= 50:
        return 2
    return 3


def aqi_level(aqi):
    if aqi is None:
        return None
    if aqi <= 20:
        return 1
    if aqi <= 40:
        return 2
    if aqi <= 60:
        return 3
    return 4


def main():
    cache = {}
    result = {"generatedAt": "", "days": {}}

    for dkey, (city, lat, lon) in LOCS.items():
        date = f"2026-{dkey.replace('/', '-')}"
        ck = f"{lat:.3f},{lon:.3f}"
        if ck not in cache:
            try:
                om = openmeteo_forecast(lat, lon)
            except Exception as e:
                print(f"open-meteo forecast error {ck}: {e}", file=sys.stderr)
                om = {}
            try:
                mn = metno_crosscheck(lat, lon)
            except Exception as e:
                print(f"met.no error {ck}: {e}", file=sys.stderr)
                mn = {}
            time.sleep(1.2)  # met.no rate limit ~1 req/sec
            try:
                aq = openmeteo_airquality(lat, lon)
            except Exception as e:
                print(f"air-quality error {ck}: {e}", file=sys.stderr)
                aq = {}
            try:
                hr = openmeteo_hourly(lat, lon)
            except Exception as e:
                print(f"hourly error {ck}: {e}", file=sys.stderr)
                hr = {}
            cache[ck] = {"om": om, "mn": mn, "aq": aq, "hr": hr}
        om = cache[ck]["om"]
        mn = cache[ck]["mn"]
        aq = cache[ck]["aq"]
        hr = cache[ck]["hr"]

        entry = {"city": city}
        omday = om.get(date)
        if omday and omday["hi"] is not None:
            hi = round(omday["hi"])
            lo = round(omday["lo"])
            if mn.get(date):
                hi = round((hi + round(mn[date]["hi"])) / 2) if mn[date].get("hi") is not None else hi
                lo = round((lo + round(mn[date]["lo"])) / 2) if mn[date].get("lo") is not None else lo
            entry.update({
                "live": True,
                "hi": hi, "lo": lo,
                "code": omday["code"],
                "rain": omday["rain"],
                "wind": round(omday["wind"], 1) if omday["wind"] is not None else None,
                "gust": round(omday["gust"], 1) if omday["gust"] is not None else None,
            })
        else:
            entry["live"] = False

        if hr.get(date):
            entry["hourly"] = hr[date]

        aqday = aq.get(date)
        if aqday:
            entry.update({
                "aqi": aqday["aqi"],
                "aqiLevel": aqi_level(aqday["aqi"]),
                "pm25": aqday["pm25"],
            })
            p = aqday["pollen"]
            pl = {k: pollen_level(v) for k, v in p.items()}
            entry["pollen"] = p
            entry["pollenLevel"] = max(pl.values()) if pl else 0

        result["days"][date] = entry

    import datetime as dt
    result["generatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()

    out = __import__('os').path.join(BASE, "weather_live.json")
    json.dump(result, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {out} with {len(result['days'])} days")


if __name__ == "__main__":
    main()
