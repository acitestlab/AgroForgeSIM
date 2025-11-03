import csv, json, math
from pathlib import Path

START_E = 563_673.025    # meters (from your sheet)
START_N = 767_918.069    # meters (from your sheet)
UTM_ZONE = 31            # Ogun State -> UTM 31N => EPSG:32631

CSV_PATH = Path("Survey_Segment_Data_with_Bearings.csv")  # your uploaded CSV name
OUT_DIR = Path(".")

def parse_bearing_to_azimuth(bearing: str) -> float:
    """
    Convert quadrant bearings like 'N 34° E' to azimuth degrees.
    0°=N, 90°=E, 180°=S, 270°=W. Degree symbol/spaces are flexible.
    Also accepts plain numbers (already azimuth).
    """
    b = bearing.strip().upper().replace("DEG", "").replace("°", "")
    import re
    m = re.match(r'^\s*([NS])\s*([0-9]+(?:\.[0-9]*)?)\s*([EW])\s*$', b)
    if m:
        a, ang, bdir = m.groups()
        ang = float(ang)
        if a == "N" and bdir == "E": return ang
        if a == "S" and bdir == "E": return 180.0 - ang
        if a == "S" and bdir == "W": return 180.0 + ang
        if a == "N" and bdir == "W": return (360.0 - ang) % 360.0
    try:
        return float(b)  # already azimuth
    except:
        raise ValueError(f"Unrecognized bearing format: {bearing!r}")

def read_segments(csv_path: Path):
    with open(csv_path, "r", encoding="utf-8") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        import csv as _csv
        try:
            dialect = _csv.Sniffer().sniff(sample)
        except Exception:
            dialect = _csv.excel
        rdr = csv.DictReader(fh, dialect=dialect)
        segs = []
        for row in rdr:
            # find bearing field
            bearing = None
            for k in row.keys():
                if "bear" in k.lower() or "azim" in k.lower():
                    bearing = row[k]
                    break
            if bearing is None:
                raise ValueError("CSV must have a 'bearing' or 'azimuth' column.")
            # find distance field
            dist = None
            for k in row.keys():
                lk = k.lower()
                if lk in ("distance", "distance_m", "distance (m)"):
                    dist = row[k]
                    break
            if dist is None:
                # fallback: first numeric not the bearing column
                for k,v in row.items():
                    if k == bearing: continue
                    try:
                        float(v); dist = v; break
                    except: pass
            if dist is None:
                raise ValueError("CSV must include a distance column (meters).")
            segs.append((parse_bearing_to_azimuth(str(bearing)), float(dist)))
        return segs

def walk_vertices(start_e, start_n, segments):
    pts = [(start_e, start_n)]
    E, N = start_e, start_n
    for az, dist in segments:
        t = math.
