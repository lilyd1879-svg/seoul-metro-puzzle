"""
Generate Certified Unique-Solution Puzzles for the Sejong City Bus & BRT Network.
Every stage is mathematically verified via bounded simple-path search to have
EXACTLY ONE valid path satisfying all its clues.
"""

import json
import math
import random
from collections import defaultdict
from sejong_bus_data import (
    STOPS_COORDS, LINES, LINE_COLORS, STREAM_CROSSINGS,
    WEST_BANK, EAST_BANK
)


def build_stations_dict():
    stations = {}
    for name, (x, y) in STOPS_COORDS.items():
        stations[name] = {
            "x": float(x),
            "y": float(y),
            "lines": [],
            "bank": "west" if name in WEST_BANK else "east"
        }
    for line_name, seq in LINES.items():
        for st in seq:
            if line_name not in stations[st]["lines"]:
                stations[st]["lines"].append(line_name)
    return stations


def gentle_spread(stations):
    names = list(stations.keys())
    min_dist = 105.0
    for _ in range(100):
        moved = False
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1, n2 = names[i], names[j]
                if stations[n1]["bank"] != stations[n2]["bank"]:
                    # Keep North and South banks separated across Geumgang
                    continue
                dx = stations[n1]["x"] - stations[n2]["x"]
                dy = stations[n1]["y"] - stations[n2]["y"]
                if abs(dx) >= min_dist or abs(dy) >= min_dist:
                    continue
                d = math.hypot(dx, dy)
                if d < min_dist:
                    moved = True
                    ux, uy = (dx / d, dy / d) if d > 0.1 else (1.0, 0.0)
                    push = (min_dist - d) * 0.4
                    stations[n1]["x"] = round(stations[n1]["x"] + ux * push, 1)
                    stations[n1]["y"] = round(stations[n1]["y"] + uy * push, 1)
                    stations[n2]["x"] = round(stations[n2]["x"] - ux * push, 1)
                    stations[n2]["y"] = round(stations[n2]["y"] - uy * push, 1)
        if not moved:
            break


def optimize_labels(stations):
    placed_boxes = []
    candidates = [
        (0, -18, "middle"), (0, 24, "middle"), (14, 5, "start"), (-14, 5, "end"),
        (12, -14, "start"), (-12, -14, "end"), (12, 22, "start"), (-12, 22, "end"),
        (0, -30, "middle"), (0, 36, "middle"), (22, 5, "start"), (-22, 5, "end")
    ]
    station_circles = [(st["x"] - 10, st["y"] - 10, st["x"] + 10, st["y"] + 10) for st in stations.values()]

    def overlap(b1, b2):
        return max(0, min(b1[2], b2[2]) - max(b1[0], b2[0])) * max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))

    for name in sorted(stations.keys(), key=lambda n: -len(stations[n]["lines"])):
        st = stations[name]
        x, y = st["x"], st["y"]
        w, h = len(name) * 12 + 6, 17
        best_cand = None
        best_score = 999999

        for dx, dy, anchor in candidates:
            lx, ly = x + dx, y + dy
            if anchor == "middle":
                box = (lx - w / 2, ly - h + 2, lx + w / 2, ly + 2)
            elif anchor == "start":
                box = (lx, ly - h + 2, lx + w, ly + 2)
            else:
                box = (lx - w, ly - h + 2, lx, ly + 2)

            score = sum(
                overlap(box, pb) * 10
                for pb in placed_boxes
                if not (box[2] < pb[0] or box[0] > pb[2] or box[3] < pb[1] or box[1] > pb[3])
            )
            score += sum(
                overlap(box, sc) * 5
                for sc in station_circles
                if not (box[2] < sc[0] or box[0] > sc[2] or box[3] < sc[1] or box[1] > sc[3])
            )
            score += (abs(dx) + abs(dy)) * 0.05
            if score < best_score:
                best_score = score
                best_cand = (dx, dy, anchor, box)
                if score < 0.8:
                    break
        dx, dy, anchor, best_box = best_cand
        placed_boxes.append(best_box)
        st["lx"], st["ly"], st["anchor"] = round(x + dx, 1), round(y + dy, 1), anchor


def build_graph():
    adj = defaultdict(list)
    for line, seq in LINES.items():
        for i in range(len(seq) - 1):
            u, v = seq[i], seq[i + 1]
            adj[u].append((v, line))
            adj[v].append((u, line))
    return adj


def get_valid_line_sequences(path, adj):
    if len(path) < 2:
        return [[]]
    u0, u1 = path[0], path[1]
    init_lines = sorted(set(l for nbr, l in adj[u0] if nbr == u1))
    dp = {l: [[l]] for l in init_lines}

    for i in range(1, len(path) - 1):
        u, v = path[i], path[i + 1]
        valid_lines = sorted(set(l for nbr, l in adj[u] if nbr == v))
        next_dp = {}
        for l_next in valid_lines:
            best_len = 9999
            best_seqs = []
            for l_prev, seqs_prev in dp.items():
                for seq_prev in seqs_prev:
                    cand = seq_prev if l_prev == l_next else seq_prev + [l_next]
                    if len(cand) < best_len:
                        best_len = len(cand)
                        best_seqs = [cand]
                    elif len(cand) == best_len and cand not in best_seqs:
                        best_seqs.append(cand)
            if best_seqs:
                next_dp[l_next] = best_seqs
        dp = next_dp

    all_min = []
    min_len = 9999
    for seq_list in dp.values():
        for s in seq_list:
            if len(s) < min_len:
                min_len = len(s)
                all_min = [s]
            elif len(s) == min_len and s not in all_min:
                all_min.append(s)
    return all_min


def analyze_path(path, adj):
    river = sum(1 for i in range(len(path) - 1) if (path[i], path[i + 1]) in STREAM_CROSSINGS)
    seqs = get_valid_line_sequences(path, adj)
    transfers = len(seqs[0]) - 1 if seqs and seqs[0] else 0
    return transfers, river, seqs


def find_simple_paths(adj, start, end, exact_len, max_paths=300):
    results = []
    visited = {start}
    path = [start]

    def dfs(curr):
        if len(results) >= max_paths:
            return
        if len(path) == exact_len:
            if curr == end:
                results.append(list(path))
            return
        if curr == end:
            return
        # Deduplicate neighbors
        seen_nbrs = set()
        for nbr, _ in adj[curr]:
            if nbr in seen_nbrs or nbr in visited:
                continue
            seen_nbrs.add(nbr)
            visited.add(nbr)
            path.append(nbr)
            dfs(nbr)
            path.pop()
            visited.remove(nbr)

    dfs(start)
    return results


def path_satisfies_clues(path, clues, adj):
    transfers, river, seqs = analyze_path(path, adj)
    for c in clues:
        t, v = c["type"], c["val"]
        if t == "total_stations" and len(path) != v:
            return False
        elif t == "transfer_count" and transfers != v:
            return False
        elif t == "river_crossings" and river != v:
            return False
        elif t == "via_station" and v not in path:
            return False
        elif t == "avoid_station" and v in path:
            return False
        elif t == "uses_line" and not any(v in s for s in seqs):
            return False
        elif t == "line_sequence" and not any(s == v for s in seqs):
            return False
    return True


def make_clue_obj(ctype, val):
    if ctype == "total_stations":
        return {"type": ctype, "val": val, "text": f"출발·도착 포함 총 {val}개 정류장 정차"}
    if ctype == "transfer_count":
        return {"type": ctype, "val": val, "text": f"최소 노선 환승 {val}회"}
    if ctype == "river_crossings":
        if val == 0:
            return {"type": ctype, "val": val, "text": "방축천을 건너지 않음 (횡단 0회)"}
        return {"type": ctype, "val": val, "text": f"방축천 다리 총 {val}회 횡단"}
    if ctype == "via_station":
        return {"type": ctype, "val": val, "text": f"'{val}' 정류장 반드시 경유"}
    if ctype == "avoid_station":
        return {"type": ctype, "val": val, "text": f"'{val}' 정류장 경유 금지"}
    if ctype == "uses_line":
        return {"type": ctype, "val": val, "text": f"'{val}' 노선 반드시 탑승"}
    if ctype == "line_sequence":
        return {"type": ctype, "val": val, "text": f"노선 순서: {' ➔ '.join(val)}"}
    raise ValueError(ctype)


THEMES = {
    "쉬움": [
        ("정부세종청사 출근길", "어진동 청사와 도담동·아름동을 잇는 생활권 버스 노선을 추적하세요."),
        ("1생활권 마실", "고운동·아름동·종촌동 단지와 복합커뮤니티센터를 연결하는 순환 경로입니다."),
        ("세종호수공원 나들이", "국립세종도서관과 호수공원으로 향하는 직통 노선을 추리하세요."),
        ("충남대병원 통원길", "도담동과 1생활권 각 단지를 연결하는 빠른 버스 경로입니다."),
    ],
    "중간": [
        ("방축천을 건너는 통학", "고운·아름·종촌동과 도담·어진동 학교·청사를 환승으로 연결하세요."),
        ("201·202번 순환 연계", "1생활권 외곽순환과 내부순환 버스의 환승 거점을 찾아내세요."),
        ("도담·어진 청사 순회", "정부세종청사 북측·중앙동·남측과 인근 기관을 오가는 최적 경로입니다."),
        ("아름동·종촌동 학원가", "가재마을과 범지기마을을 잇는 생활권 지선 환승 퍼즐입니다."),
    ],
    "어려움": [
        ("1생활권 다중 환승 챌린지", "정류장 수와 환승 횟수, 방축천 횡단 조건을 모두 만족하는 유일한 경로입니다."),
        ("고운동·어진동 우회 추리", "특정 정류장 경유를 피해 201·202·221·1000번을 조합해야 합니다."),
        ("방축천 입체 환승", "지선·순환·광역버스를 정교하게 환승해 목적지까지 도달하세요."),
    ],
    "초고난이도": [
        ("1생활권 마스터 내비게이터", "노선 순서 힌트 없이 오직 정황 단서만으로 유일한 버스 경로를 복원하세요."),
        ("1생활권 마지막 막차", "고운·아름·종촌·도담·어진 5개 동을 넘나드는 고난도 다중 환승 퍼즐입니다."),
    ],
}


def generate_tier_puzzles(adj, stations, diff, min_len, max_len, min_tr, max_tr, target_count, rng, allow_line_seq=True):
    stops = list(stations.keys())
    stages = []
    used_pairs = set()
    attempts = 0

    while len(stages) < target_count and attempts < 4000:
        attempts += 1
        start = rng.choice(stops)
        end = rng.choice(stops)
        if start == end or (start, end) in used_pairs:
            continue

        target_len = rng.randint(min_len, max_len)
        all_paths = find_simple_paths(adj, start, end, target_len, max_paths=250)
        if not all_paths or len(all_paths) >= 250:
            continue

        # Pick a candidate path matching transfer range
        rng.shuffle(all_paths)
        chosen = None
        for p in all_paths:
            tr, rv, seqs = analyze_path(p, adj)
            if min_tr <= tr <= max_tr:
                chosen = (p, tr, rv, seqs)
                break
        if not chosen:
            continue

        p, tr, rv, seqs = chosen
        base_clues = [
            make_clue_obj("total_stations", len(p)),
            make_clue_obj("transfer_count", tr),
        ]

        # Build candidate extra clues
        extra_pool = []
        if rv > 0 or diff in ("어려움", "초고난이도"):
            extra_pool.append(make_clue_obj("river_crossings", rv))

        if seqs and seqs[0]:
            if allow_line_seq and diff in ("쉬움", "중간") and len(seqs[0]) <= 3:
                extra_pool.append(make_clue_obj("line_sequence", seqs[0]))
            for l in seqs[0]:
                extra_pool.append(make_clue_obj("uses_line", l))

        mids = p[1:-1]
        if mids:
            for m in rng.sample(mids, min(2, len(mids))):
                extra_pool.append(make_clue_obj("via_station", m))

        # Find avoid_station candidates from other paths
        other_mids = set()
        for op in all_paths:
            if op != p:
                for st in op[1:-1]:
                    if st not in p:
                        other_mids.add(st)
        for av in rng.sample(list(other_mids), min(2, len(other_mids))):
            extra_pool.append(make_clue_obj("avoid_station", av))

        # Greedily add clues until unique
        clues = list(base_clues)
        matching = [op for op in all_paths if path_satisfies_clues(op, clues, adj)]
        for ec in extra_pool:
            if len(matching) == 1:
                break
            # Avoid duplicate clue types on same value
            if any(c["type"] == ec["type"] and c["val"] == ec["val"] for c in clues):
                continue
            test_clues = clues + [ec]
            test_matching = [op for op in matching if path_satisfies_clues(op, [ec], adj)]
            if len(test_matching) < len(matching) and p in test_matching:
                clues = test_clues
                matching = test_matching

        if len(matching) == 1 and matching[0] == p and len(clues) <= 6:
            used_pairs.add((start, end))
            used_pairs.add((end, start))
            title, story = rng.choice(THEMES[diff])
            stages.append({
                "id": f"sj-{diff}-{len(stages)+1}",
                "difficulty": diff,
                "title": f"{title} #{len(stages)+1}",
                "story": story,
                "start": start,
                "end": end,
                "path_length": len(p),
                "min_transfers": tr,
                "river_crossings": rv,
                "solution": p,
                "solution_lines": seqs[0] if seqs else [],
                "clues": clues,
            })

    return stages


def main():
    rng = random.Random(20261114)
    stations = build_stations_dict()
    gentle_spread(stations)
    optimize_labels(stations)
    adj = build_graph()

    stages = []
    stages += generate_tier_puzzles(adj, stations, "쉬움", 4, 6, 0, 1, 10, rng, allow_line_seq=True)
    stages += generate_tier_puzzles(adj, stations, "중간", 6, 8, 1, 2, 10, rng, allow_line_seq=True)
    stages += generate_tier_puzzles(adj, stations, "어려움", 8, 10, 2, 4, 10, rng, allow_line_seq=False)
    stages += generate_tier_puzzles(adj, stations, "초고난이도", 10, 13, 3, 5, 9, rng, allow_line_seq=False)

    # Final audit of every stage
    for stg in stages:
        all_paths = find_simple_paths(adj, stg["start"], stg["end"], stg["path_length"], max_paths=500)
        valid = [p for p in all_paths if path_satisfies_clues(p, stg["clues"], adj)]
        assert len(valid) == 1, f"Stage {stg['id']} not unique: {len(valid)}"
        assert valid[0] == stg["solution"], f"Stage {stg['id']} solution mismatch"

    counts = defaultdict(int)
    for s in stages:
        counts[s["difficulty"]] += 1
    print("Generated certified Sejong Bus stages:", dict(counts), "Total:", len(stages))

    game_data = {
        "stations": stations,
        "lines": LINES,
        "line_colors": LINE_COLORS,
        "stages": stages,
    }
    with open("scripts/sejong_bus/sejong_game_data.json", "w", encoding="utf-8") as f:
        json.dump(game_data, f, ensure_ascii=False, indent=2)
    print("Saved scripts/sejong_bus/sejong_game_data.json")


if __name__ == "__main__":
    main()
