#!/usr/bin/env python3
"""Monitor public eBird Sandhill crane observations near Glasgow, KY."""
import json, os, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

BASE=Path(__file__).parent
DATA=BASE/"site"/"data.json"
CENTERS=[(37.0004,-85.9200),(36.928947,-86.029818)]
NOW=datetime.now(timezone.utc)
LOCAL=ZoneInfo("America/Chicago")
KEY=os.getenv("EBIRD_API_KEY","").strip()
TOPIC=os.getenv("NTFY_TOPIC","").strip()
THRESHOLD=int(os.getenv("ALERT_THRESHOLD","500"))
RADIUS=max(5,min(50,int(os.getenv("RADIUS_KM","25"))))

def observation_time(value):
    try: return datetime.strptime(value[:16],"%Y-%m-%d %H:%M").replace(tzinfo=LOCAL).astimezone(timezone.utc)
    except (ValueError,TypeError): return None

def fetch(lat,lon):
    query=urllib.parse.urlencode({"lat":lat,"lng":lon,"dist":RADIUS,"back":3,"maxResults":1000})
    req=urllib.request.Request("https://api.ebird.org/v2/data/obs/geo/recent/sancra?"+query,
        headers={"X-eBirdApiToken":KEY,"User-Agent":"GlasgowCraneWatch/1.0"})
    with urllib.request.urlopen(req,timeout=30) as res: return json.load(res)

def notify(message):
    req=urllib.request.Request("https://ntfy.sh/"+urllib.parse.quote(TOPIC,safe=""),
        data=message.encode(),method="POST",
        headers={"Title":"Crane Watch: high activity","Priority":"high","Tags":"bird"})
    with urllib.request.urlopen(req,timeout=20): pass

def main():
    old={}
    if DATA.exists():
        try: old=json.loads(DATA.read_text())
        except (ValueError,OSError): pass
    if not KEY: raise RuntimeError("Missing EBIRD_API_KEY secret")
    try:
        unique={}
        for lat,lon in CENTERS:
            for item in fetch(lat,lon):
                if item.get("speciesCode")!="sancra": continue
                identity="|".join(str(item.get(k,"")) for k in ("subId","locId","obsDt"))
                unique[identity]=item
        sites={}
        for item in unique.values():
            observed=observation_time(item.get("obsDt"))
            if not observed or not timedelta(0)<=NOW-observed<=timedelta(hours=48): continue
            r={"place":item.get("locName","Unknown"),"count":max(0,int(item.get("howMany") or 0)),
               "date":item.get("obsDt"),"lat":item.get("lat"),"lng":item.get("lng"),"id":item.get("subId","")}
            place_id=(r["lat"],r["lng"])
            if place_id not in sites or r["date"]>sites[place_id]["date"]: sites[place_id]=r
        reports=sorted(sites.values(),key=lambda r:(r["count"],r["date"]),reverse=True)
        recent=[r for r in reports if NOW-observation_time(r["date"])<=timedelta(hours=24)]
        peak=max((r["count"] for r in reports),default=0)>=THRESHOLD or sum(r["count"]>=100 for r in reports)>=3
        trigger=any(r["count"]>=THRESHOLD for r in recent) or sum(r["count"]>=100 for r in recent)>=3
        previous=old.get("last_alert_at")
        last=datetime.fromisoformat(previous.replace("Z","+00:00")) if previous else None
        due=not last or NOW-last>=timedelta(hours=24)
        alerted=False
        if trigger and due and TOPIC:
            notify("Large Sandhill crane reports near Glasgow and Barren River Lake. Largest reported flock: "+format(max(r["count"] for r in recent),",")+". Reports are not live bird counts.")
            alerted=True
        history=old.get("history",[])[-335:]
        history.append({"time":NOW.isoformat(),"largest":max((r["count"] for r in reports),default=0),"sites":len(reports),"peak":peak})
        result={"last_checked":NOW.isoformat(),"status":"ok","threshold":THRESHOLD,"radius_km":RADIUS,
            "peak":peak,"largest":max((r["count"] for r in reports),default=0),"sites":len(reports),
            "reports":reports[:80],"history":history[-336:],"last_alert_at":NOW.isoformat() if alerted else previous,
            "alerts_enabled":bool(TOPIC)}
    except Exception as ex:
        result={**old,"last_checked":NOW.isoformat(),"status":"error","error":str(ex)[:200]}
        print("Monitoring error:",result["error"])
    DATA.parent.mkdir(parents=True,exist_ok=True)
    DATA.write_text(json.dumps(result,indent=2)+"\n")
    print("Monitor status:",result.get("status"),"sites:",result.get("sites"))

if __name__=="__main__": main()
