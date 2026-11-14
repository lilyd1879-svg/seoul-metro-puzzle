"""
Rigorous Puzzle Search and Verification Engine for Seoul Metro
Finds paths, applies clue predicates, and verifies:
1) Solution count == 1 (Unique solution)
2) Minimality: Removing any single clue yields > 1 solution.
"""

import json
from collections import defaultdict, deque
from metro_data import STATIONS, LINES, HAN_RIVER_CROSSINGS, LINE_COLORS

def build_graph():
    # adj[u] = list of (v, line)
    adj = defaultdict(list)
    for line, seq in LINES.items():
        for i in range(len(seq) - 1):
            u, v = seq[i], seq[i+1]
            if u in STATIONS and v in STATIONS:
                adj[u].append((v, line))
                adj[v].append((u, line))
    return adj

def get_line_sequence(path, adj):
    """
    Given a station path [s0, s1, ..., sk], determine the line sequence.
    If multiple lines run between u and v, find a valid consistent line assignment.
    """
    # Find all valid line sequences for this station sequence
    def search_lines(idx, current_lines):
        if idx == len(path) - 1:
            return [current_lines]
        u, v = path[idx], path[idx+1]
        valid_lines = [l for neighbor, l in adj[u] if neighbor == v]
        results = []
        for l in set(valid_lines):
            res = search_lines(idx + 1, current_lines + [l])
            results.extend(res)
        return results

    all_line_seqs = search_lines(0, [])
    # Compress consecutive same lines: ['2호선', '2호선', '3호선'] -> ['2호선', '3호선']
    unique_compressed = []
    for seq in all_line_seqs:
        comp = []
        for l in seq:
            if not comp or comp[-1] != l:
                comp.append(l)
        if comp not in unique_compressed:
            unique_compressed.append(comp)
    return unique_compressed

def count_river_crossings(path):
    crossings = 0
    for i in range(len(path) - 1):
        pair = (path[i], path[i+1])
        if pair in HAN_RIVER_CROSSINGS:
            crossings += 1
    return crossings

def find_all_simple_paths(start, end, max_len=14):
    adj = build_graph()
    results = []
    
    def dfs(current, visited):
        if len(visited) > max_len:
            return
        if current == end:
            results.append(list(visited))
            return
        for neighbor, _ in adj[current]:
            if neighbor not in visited:
                visited.append(neighbor)
                dfs(neighbor, visited)
                visited.pop()

    dfs(start, [start])
    return results

def evaluate_puzzle(start, end, clues, all_paths, adj):
    """
    Evaluates whether clues produce a unique solution.
    clues is a dict of:
    - 'station_count': int
    - 'line_seq': list of str
    - 'river_crossings': int
    - 'avoid_station': str
    - 'must_pass': str
    - 'transfer_count': int
    """
    matching_paths = []
    for path in all_paths:
        match = True
        
        if 'station_count' in clues:
            if len(path) != clues['station_count']:
                match = False
                
        if match and 'river_crossings' in clues:
            if count_river_crossings(path) != clues['river_crossings']:
                match = False
                
        if match and 'avoid_station' in clues:
            if clues['avoid_station'] in path:
                match = False

        if match and 'must_pass' in clues:
            if clues['must_pass'] not in path:
                match = False

        if match and ('line_seq' in clues or 'transfer_count' in clues):
            comp_seqs = get_line_sequence(path, adj)
            
            if 'line_seq' in clues:
                if clues['line_seq'] not in comp_seqs:
                    match = False
                    
            if match and 'transfer_count' in clues:
                has_transfer_match = any((len(seq) - 1) == clues['transfer_count'] for seq in comp_seqs)
                if not has_transfer_match:
                    match = False

        if match:
            matching_paths.append(path)
            
    return matching_paths

def check_minimality(start, end, clues, all_paths, adj):
    """
    Verifies that removing ANY single clue from clues produces > 1 solution.
    """
    if len(clues) <= 1:
        return False
        
    for k in list(clues.keys()):
        reduced = {rk: rv for rk, rv in clues.items() if rk != k}
        paths = evaluate_puzzle(start, end, reduced, all_paths, adj)
        if len(paths) <= 1:
            # Removing this clue still yielded 1 (or 0) solution -> clue k is redundant!
            return False
    return True

def search_candidates():
    adj = build_graph()
    
    # Candidate OD pairs
    test_pairs = [
        # Easy candidates
        ("홍대입구", "시청", 8),
        ("여의도", "강남", 12),
        ("종로3가", "고속터미널", 10),
        ("합정", "노량진", 9),
        ("동대문", "강남", 12),
        ("신도림", "삼각지", 10),
        ("건대입구", "압구정", 8),
        ("을지로3가", "여의도", 10),
        ("왕십리", "신논현", 12),
        ("시청", "고속터미널", 11),
    ]
    
    verified_puzzles = []

    for start, end, max_len in test_pairs:
        all_paths = find_all_simple_paths(start, end, max_len)
        print(f"\nChecking {start} -> {end}: Found {len(all_paths)} simple paths (max_len={max_len})")
        if not all_paths:
            continue
            
        # Try to find minimal clue puzzles for this pair
        for path in all_paths:
            comp_seqs = get_line_sequence(path, adj)
            if not comp_seqs:
                continue
            line_seq = comp_seqs[0]
            st_cnt = len(path)
            rc = count_river_crossings(path)
            transfers = len(line_seq) - 1

            # Candidate clue combinations
            candidate_clue_sets = [
                # Clue set 1: station_count + line_seq
                {"station_count": st_cnt, "line_seq": line_seq},
                # Clue set 2: station_count + line_seq + river_crossings
                {"station_count": st_cnt, "line_seq": line_seq, "river_crossings": rc},
                # Clue set 3: station_count + transfer_count + river_crossings
                {"station_count": st_cnt, "transfer_count": transfers, "river_crossings": rc},
            ]
            
            # Add avoid_station candidates
            for station in STATIONS:
                if station not in path and station in ["시청", "고속터미널", "여의도", "용산", "충무로", "당산"]:
                    candidate_clue_sets.append({
                        "station_count": st_cnt,
                        "line_seq": line_seq,
                        "avoid_station": station
                    })
                    candidate_clue_sets.append({
                        "station_count": st_cnt,
                        "transfer_count": transfers,
                        "river_crossings": rc,
                        "avoid_station": station
                    })

            for clues in candidate_clue_sets:
                matches = evaluate_puzzle(start, end, clues, all_paths, adj)
                if len(matches) == 1:
                    if check_minimality(start, end, clues, all_paths, adj):
                        # Verified Minimal Unique Puzzle!
                        puz = {
                            "start": start,
                            "end": end,
                            "solution_path": matches[0],
                            "clues": clues,
                            "all_paths_count": len(all_paths),
                            "transfers": transfers,
                            "length": st_cnt
                        }
                        # Check duplicate
                        if not any(p["start"] == start and p["end"] == end and p["solution_path"] == matches[0] for p in verified_puzzles):
                            verified_puzzles.append(puz)
                            print(f"  [FOUND] {start} -> {end} | Path: {'->'.join(matches[0])} | Clues: {clues}")
                            break
                            
    return verified_puzzles

if __name__ == "__main__":
    puzzles = search_candidates()
    print(f"\nTotal verified minimal unique puzzles found: {len(puzzles)}")
    with open("scripts/verified_puzzles.json", "w", encoding="utf-8") as f:
        json.dump(puzzles, f, ensure_ascii=False, indent=2)
