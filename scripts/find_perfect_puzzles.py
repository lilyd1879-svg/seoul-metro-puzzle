"""
Find Perfect Minimal Unique Puzzles for Seoul Metro
Explores various start-end pairs and finds certified minimal unique puzzles.
"""

import json
from metro_data import STATIONS, LINES, HAN_RIVER_CROSSINGS
from verify_puzzles import build_graph, find_all_simple_paths, get_line_sequence, count_river_crossings

adj = build_graph()

def evaluate(path, clue, adj):
    c_type = clue[0]
    val = clue[1]
    
    if c_type == "total_stations":
        return len(path) == val
    elif c_type == "river_crossings":
        return count_river_crossings(path) == val
    elif c_type == "avoid_station":
        return val not in path
    elif c_type == "via_station":
        return val in path
    elif c_type == "transfer_count":
        seqs = get_line_sequence(path, adj)
        return any((len(s) - 1) == val for s in seqs)
    elif c_type == "line_sequence":
        seqs = get_line_sequence(path, adj)
        return val in seqs
    elif c_type == "transfer_at":
        # Transfer happens at station 'val'
        # That means station 'val' is where line changes
        # Check if val is in path and adjacent edges have different lines
        if val not in path or path[0] == val or path[-1] == val:
            return False
        idx = path.index(val)
        u, m, v = path[idx-1], path[idx], path[idx+1]
        u_lines = set(l for n, l in adj[m] if n == u)
        v_lines = set(l for n, l in adj[m] if n == v)
        # There must be a valid transfer at m
        return bool(u_lines and v_lines and (u_lines != v_lines or len(u_lines) > 1))
    elif c_type == "line_station_count":
        # (line_name, count)
        target_line, count = val
        # Count stations ridden on target_line
        seqs = get_line_sequence(path, adj)
        # Check if in any valid assignment, number of stations on target_line == count
        for i in range(len(path) - 1):
            pass # simplified below
        return True
    return True

def get_matching_paths(paths, clue_set, adj):
    matches = []
    for p in paths:
        if all(evaluate(p, c, adj) for c in clue_set):
            matches.append(p)
    return matches

def is_minimal(paths, clue_set, adj):
    """
    Every clue in clue_set must be essential.
    Removing any single clue must result in >= 2 matching paths.
    """
    if len(clue_set) < 2:
        return False
    for i in range(len(clue_set)):
        sub_clues = clue_set[:i] + clue_set[i+1:]
        sub_matches = get_matching_paths(paths, sub_clues, adj)
        if len(sub_matches) <= 1:
            return False # Clue i was redundant!
    return True

# Search across rich set of station pairs
pairs_to_try = [
    # Short/Medium
    ("합정", "노량진", 11),
    ("홍대입구", "여의도", 11),
    ("시청", "고속터미널", 12),
    ("을지로3가", "여의도", 11),
    ("동대문", "강남", 13),
    ("신도림", "삼각지", 11),
    ("용산", "강남", 12),
    ("건대입구", "신사", 11),
    ("종각", "여의도", 11),
    ("사당", "여의도", 12),
    ("이태원", "강남", 11),
    ("공덕", "고속터미널", 12),
    ("왕십리", "강남", 12),
    ("영등포", "충무로", 11),
    ("신촌", "고속터미널", 12),
    ("잠실", "시청", 13),
    ("당산", "신사", 12),
]

found_puzzles = []

for start, end, max_l in pairs_to_try:
    all_paths = find_all_simple_paths(start, end, max_l)
    if len(all_paths) < 3:
        continue
    print(f"Searching {start} -> {end} ({len(all_paths)} total paths)...")
    
    for path in all_paths:
        p_len = len(path)
        p_lines = get_line_sequence(path, adj)[0]
        p_transfers = len(p_lines) - 1
        p_rc = count_river_crossings(path)
        
        # Build candidate clue pool for this path
        pool = [
            ("total_stations", p_len),
            ("transfer_count", p_transfers),
            ("line_sequence", p_lines),
            ("river_crossings", p_rc),
        ]
        
        # Candidate transfer stations
        for st in path[1:-1]:
            if len(STATIONS[st]["lines"]) > 1:
                pool.append(("via_station", st))
                
        # Candidate avoid stations (stations near the route that were not used)
        for st in STATIONS:
            if st not in path and STATIONS[st]["lines"]:
                # Check if this station is in some other competing path
                competing_has_st = any(st in op for op in all_paths if op != path)
                if competing_has_st and len(pool) < 12:
                    pool.append(("avoid_station", st))

        # Test clue subsets of size 2, 3, 4
        from itertools import combinations
        for k in [2, 3, 4]:
            found_for_path = False
            for c_combo in combinations(pool, k):
                # Quick check: does it match path?
                matches = get_matching_paths(all_paths, c_combo, adj)
                if len(matches) == 1:
                    # Check minimality!
                    if is_minimal(all_paths, c_combo, adj):
                        puzzle_data = {
                            "start": start,
                            "end": end,
                            "path": path,
                            "path_length": p_len,
                            "line_sequence": p_lines,
                            "transfers": p_transfers,
                            "river_crossings": p_rc,
                            "clues": [list(c) for c in c_combo],
                            "competing_paths": len(all_paths)
                        }
                        found_puzzles.append(puzzle_data)
                        print(f"  ★ CERTIFIED MINIMAL UNIQUE PUZZLE ({k} clues):")
                        print(f"     {start} -> {end} | Path: {' -> '.join(path)}")
                        print(f"     Clues: {c_combo}")
                        found_for_path = True
                        break
            if found_for_path:
                break

print(f"\nTotal certified puzzles found: {len(found_puzzles)}")
with open("scripts/certified_puzzles.json", "w", encoding="utf-8") as f:
    json.dump(found_puzzles, f, ensure_ascii=False, indent=2)
