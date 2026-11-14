"""
Generate 200 Completely Diverse, Non-Repeating OD Pair Puzzles (50 per tier)
- Strictly 0 duplicate (start, end) or (end, start) pairs across ALL 200 stages!
- Reuses spread-out station coordinates (>= 55.6px) and non-overlapping labels.
- 100% airtight uniqueness verification (no truncation) + strict minimality.
"""

import json
import random
from itertools import combinations
from metro_data_full import LINES, LINE_COLORS, HAN_RIVER_CROSSINGS
from spread_and_regenerate import (
    spread_stations, optimize_label_positions, build_graph, bfs_distances,
    find_all_simple_paths_exhaustive, get_line_sequence, count_river_crossings,
    evaluate, get_matching_paths, is_strictly_minimal, clue_to_text
)
from metro_data_full import STATIONS

spread_stations(STATIONS)
optimize_label_positions(STATIONS)
adj = build_graph()

all_station_names = sorted(STATIONS.keys())
random.seed(2026)

# Precompute shortest distances for fast pair filtering
dist_map = {}
for s in all_station_names:
    dist_map[s] = bfs_distances(s, adj)

used_pairs = set()

def try_find_puzzle_for_pair(start, end, target_len_min, target_len_max, difficulty, require_special=False):
    if (start, end) in used_pairs or (end, start) in used_pairs:
        return None
    d = dist_map[start].get(end, 999)
    if d < target_len_min - 1 or d > target_len_max:
        return None

    max_l = min(target_len_max, d + 4)
    all_paths_ext, trunc = find_all_simple_paths_exhaustive(start, end, max_l + 3, adj, cap=15000)
    if trunc:
        all_paths_N, trunc_N = find_all_simple_paths_exhaustive(start, end, max_l, adj, cap=15000)
        if trunc_N or len(all_paths_N) < 2:
            return None
        all_paths_ext = all_paths_N

    if len(all_paths_ext) < 3:
        return None

    cand_paths = [p for p in all_paths_ext if target_len_min <= len(p) <= max_l]
    random.shuffle(cand_paths)

    for path in cand_paths[:15]:
        p_len = len(path)
        paths_N = [p for p in all_paths_ext if len(p) <= p_len]
        if len(paths_N) < 2:
            continue

        seqs = get_line_sequence(path, adj)
        if not seqs:
            continue
        line_seq = seqs[0]
        p_transfers = len(line_seq) - 1
        p_rc = count_river_crossings(path)

        if require_special:
            special_set = {"KTX", "ITX-청춘", "무궁화호", "GTX-A", "서해선"}
            if not any(l in special_set for l in line_seq):
                continue

        sec_pool = [
            ("transfer_count", p_transfers),
            ("river_crossings", p_rc),
        ]
        if len(line_seq) <= 3:
            sec_pool.append(("line_sequence", line_seq))
        for l in line_seq:
            if l in ["KTX", "ITX-청춘", "무궁화호", "GTX-A", "서해선", "신림선", "우이신설선", "공항철도", "신분당선"]:
                sec_pool.append(("uses_line", l))
        for st in path[1:-1]:
            if len(STATIONS[st]["lines"]) > 1:
                sec_pool.append(("via_station", st))
        for st in all_station_names:
            if st not in path and len(sec_pool) < 12:
                if any(st in op for op in paths_N if op != path):
                    sec_pool.append(("avoid_station", st))

        for k in [1, 2, 3]:
            for sec_combo in combinations(sec_pool, k):
                combo = [("total_stations", p_len)] + list(sec_combo)
                matches = get_matching_paths(paths_N, combo, adj)
                if len(matches) == 1 and matches[0] == path:
                    if is_strictly_minimal(paths_N, all_paths_ext, combo, adj):
                        used_pairs.add((start, end))
                        clues_obj = [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in combo]
                        return {
                            "difficulty": difficulty,
                            "start": start,
                            "end": end,
                            "path": path,
                            "path_length": p_len,
                            "transfers": p_transfers,
                            "lines": line_seq,
                            "clues": clues_obj,
                            "competing_paths": len(paths_N)
                        }
    return None

def collect_tier(difficulty, count, min_l, max_l, require_special=False, preferred_starts=None):
    results = []
    # Build randomized candidate pairs
    starts = list(preferred_starts) if preferred_starts else list(all_station_names)
    ends = list(preferred_starts) if preferred_starts else list(all_station_names)
    pairs = []
    for s in starts:
        for e in ends:
            if s != e:
                d = dist_map[s].get(e, 999)
                if min_l - 1 <= d <= max_l:
                    pairs.append((s, e))
    random.shuffle(pairs)

    for s, e in pairs:
        if len(results) >= count:
            break
        puz = try_find_puzzle_for_pair(s, e, min_l, max_l, difficulty, require_special)
        if puz:
            puz["level"] = len(results) + 1
            puz["id"] = f"{difficulty}-{puz['level']}"
            puz["title"] = f"{s} ➔ {e} ({difficulty} #{puz['level']})"
            puz["story"] = f"{s}역에서 출발해 {e}역에 도착한 승객의 교통카드 기록입니다. 모든 단서를 충족하는 단 하나의 유일한 경로를 추리하세요."
            results.append(puz)
    print(f"★ [{difficulty}] Collected {len(results)} completely unique OD-pair stages!", flush=True)
    return results

# Special stations for Master tier (KTX/ITX/Mugunghwa/GTX-A/Seohae)
special_stations = [
    n for n, st in STATIONS.items()
    if any(l in {"KTX", "ITX-청춘", "무궁화호", "GTX-A", "서해선", "경춘선", "수인분당선"} for l in st["lines"])
] + ["홍대입구", "여의도", "강남", "고속터미널", "사당", "시청", "동대문역사문화공원", "왕십리", "건대입구", "공덕"]

master_stages = collect_tier("초고난이도", 50, 4, 8, require_special=True, preferred_starts=list(set(special_stations)))
hard_stages = collect_tier("어려움", 50, 7, 10, require_special=False)
medium_stages = collect_tier("중간", 50, 5, 7, require_special=False)
easy_stages = collect_tier("쉬움", 50, 3, 5, require_special=False)

all_stages = easy_stages + medium_stages + hard_stages + master_stages

dataset = {
    "line_colors": LINE_COLORS,
    "stations": STATIONS,
    "lines": LINES,
    "stages": all_stages
}

with open("scripts/full_game_data.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"\n★ GRAND TOTAL UNIQUE-OD STAGES: {len(all_stages)}", flush=True)
