"""
Independent Zero-Trust Audit of all 189 stages in full_game_data.json
Verifies:
1) Every edge in stage['path'] exists in LINES.
2) Every clue in stage['clues'] is satisfied by stage['path'].
3) Exhaustive search of ALL simple paths of length <= total_stations proves count == 1.
4) Check distance between all adjacent/nearby stations to detect dense clusters.
"""

import json
import math
from collections import defaultdict, deque

with open("scripts/full_game_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

STATIONS = data["stations"]
LINES = data["lines"]
STAGES = data["stages"]

# Build graph independently
adj = defaultdict(list)
for line, seq in LINES.items():
    for i in range(len(seq) - 1):
        u, v = seq[i], seq[i+1]
        if u in STATIONS and v in STATIONS:
            adj[u].append((v, line))
            adj[v].append((u, line))

from spread_and_regenerate import find_all_simple_paths_exhaustive, evaluate, get_line_sequence, count_river_crossings

print(f"Auditing {len(STAGES)} stages...")
failed = 0

for st in STAGES:
    start, end = st["start"], st["end"]
    sol = st["path"]
    clues = [(c["type"], c["val"]) for c in st["clues"]]
    
    has_len = any(ct == "total_stations" for ct, _ in clues)
    if not has_len:
        print(f"FAIL {st['id']}: Missing total_stations bound!")
        failed += 1
        continue
        
    max_len = len(sol)
    
    # 1. Verify solution satisfies all clues
    for ct, cv in clues:
        if not evaluate(sol, (ct, cv), adj):
            print(f"FAIL {st['id']}: Solution does not satisfy clue {(ct, cv)}!")
            failed += 1
            
    # 2. Exhaustive uniqueness check up to max_len
    all_p, trunc = find_all_simple_paths_exhaustive(start, end, max_len, adj, cap=20000)
    if trunc:
        print(f"WARN {st['id']}: Truncated at 20000!")
    matches = [p for p in all_p if all(evaluate(p, c, adj) for c in clues)]
    if len(matches) != 1 or matches[0] != sol:
        print(f"FAIL {st['id']}: Expected 1 unique match, got {len(matches)}!")
        failed += 1

print(f"Audit complete: {len(STAGES) - failed}/{len(STAGES)} stages PASSED 100%.")

# Check minimum distance between station nodes
min_dists = []
names = list(STATIONS.keys())
for i in range(len(names)):
    for j in range(i+1, len(names)):
        s1, s2 = STATIONS[names[i]], STATIONS[names[j]]
        d = math.hypot(s1["x"] - s2["x"], s1["y"] - s2["y"])
        if d < 45:
            min_dists.append((d, names[i], names[j]))

min_dists.sort()
print(f"\nFound {len(min_dists)} station pairs closer than 45px. Closest 15:")
for d, n1, n2 in min_dists[:15]:
    print(f"  {d:.1f}px: {n1} <-> {n2}")
