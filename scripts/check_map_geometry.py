"""
Check map geometry and topology for any visual/graph defects:
1. Isolated stations (0 connections in LINES)
2. Backtracking / 180-degree U-turns on the same line (dot product < -0.85)
3. Lines passing too close (< 18px) to non-adjacent station dots
"""
import math
from collections import defaultdict
from metro_data_v2 import STATIONS, LINES

# 1. Check isolated stations
connected = set()
for line, seq in LINES.items():
    for s in seq:
        connected.add(s)

isolated = [s for s in STATIONS if s not in connected]
print(f"Isolated stations ({len(isolated)}): {isolated}")

# 2. Check backtracking / U-turns on the same line
print("\nChecking 180-degree U-turns / backtracking on lines:")
for line, seq in LINES.items():
    for i in range(len(seq) - 2):
        u, m, v = seq[i], seq[i+1], seq[i+2]
        if u not in STATIONS or m not in STATIONS or v not in STATIONS:
            continue
        ux, uy = STATIONS[m]["x"] - STATIONS[u]["x"], STATIONS[m]["y"] - STATIONS[u]["y"]
        vx, vy = STATIONS[v]["x"] - STATIONS[m]["x"], STATIONS[v]["y"] - STATIONS[m]["y"]
        du, dv = math.hypot(ux, uy), math.hypot(vx, vy)
        if du > 0 and dv > 0:
            cos_a = (ux * vx + uy * vy) / (du * dv)
            if cos_a < -0.8:
                print(f"  [U-TURN] {line}: {u} -> {m} -> {v} (cos={cos_a:.2f})")

# 3. Check if any track segment passes close (< 18px) to a station not on that segment
def dist_point_to_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx*dx + dy*dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1)*dx + (py - y1)*dy) / l2))
    projx, projy = x1 + t*dx, y1 + t*dy
    return math.hypot(px - projx, py - projy)

print("\nChecking tracks passing right through unrelated stations (< 18px):")
for line, seq in LINES.items():
    for i in range(len(seq) - 1):
        u, v = seq[i], seq[i+1]
        if u not in STATIONS or v not in STATIONS:
            continue
        x1, y1 = STATIONS[u]["x"], STATIONS[u]["y"]
        x2, y2 = STATIONS[v]["x"], STATIONS[v]["y"]
        for s_name, st in STATIONS.items():
            if s_name == u or s_name == v:
                continue
            d = dist_point_to_seg(st["x"], st["y"], x1, y1, x2, y2)
            if d < 18:
                print(f"  [COLLISION] {line} ({u} -> {v}) passes {d:.1f}px from '{s_name}'")
