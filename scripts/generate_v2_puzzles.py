"""
Generate 200 Diverse, Airtight Unique Puzzles using metro_data_v2 (Official Map Layout & Accurate GTX-A)
"""

import json
import math
import random
from collections import defaultdict, deque
from itertools import combinations
from metro_data_v2 import STATIONS, LINES, LINE_COLORS, HAN_RIVER_CROSSINGS

# Gentle spacing pass on non-Line-2 stations if any pair < 45px, keeping Line 2 circle intact
def gentle_spread(stations):
    names = list(stations.keys())
    line2_set = set(LINES["2호선"])
    min_dist = 46.0
    for _ in range(100):
        moved = False
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1, n2 = names[i], names[j]
                dx = stations[n1]["x"] - stations[n2]["x"]
                dy = stations[n1]["y"] - stations[n2]["y"]
                d = math.hypot(dx, dy)
                if d < min_dist:
                    moved = True
                    ux, uy = (dx/d, dy/d) if d > 0.1 else (1.0, 0.0)
                    push = (min_dist - d) * 0.4
                    if n1 not in line2_set:
                        stations[n1]["x"] = round(stations[n1]["x"] + ux * push, 1)
                        stations[n1]["y"] = round(stations[n1]["y"] + uy * push, 1)
                    if n2 not in line2_set:
                        stations[n2]["x"] = round(stations[n2]["x"] - ux * push, 1)
                        stations[n2]["y"] = round(stations[n2]["y"] - uy * push, 1)
        if not moved:
            break

    closest = 9999
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = math.hypot(stations[names[i]]["x"] - stations[names[j]]["x"],
                           stations[names[i]]["y"] - stations[names[j]]["y"])
            if d < closest:
                closest = d
    print(f"Gentle spread complete. Minimum station distance: {closest:.1f}px", flush=True)

def optimize_labels(stations):
    placed_boxes = []
    candidates = [
        (0, -12, "middle"), (0, 18, "middle"), (11, 3, "start"), (-11, 3, "end"),
        (9, -10, "start"), (-9, -10, "end"), (9, 16, "start"), (-9, 16, "end"),
        (0, -21, "middle"), (0, 27, "middle"), (18, 3, "start"), (-18, 3, "end")
    ]
    station_circles = [(st["x"] - 6, st["y"] - 6, st["x"] + 6, st["y"] + 6) for st in stations.values()]

    def overlap(b1, b2):
        return max(0, min(b1[2], b2[2]) - max(b1[0], b2[0])) * max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))

    for name in sorted(stations.keys(), key=lambda n: -len(stations[n]["lines"])):
        st = stations[name]
        x, y = st["x"], st["y"]
        w, h = len(name) * 10 + 4, 13
        best_cand = None
        best_score = 999999

        for dx, dy, anchor in candidates:
            lx, ly = x + dx, y + dy
            if anchor == "middle":
                box = (lx - w/2, ly - h + 2, lx + w/2, ly + 2)
            elif anchor == "start":
                box = (lx, ly - h + 2, lx + w, ly + 2)
            else:
                box = (lx - w, ly - h + 2, lx, ly + 2)

            score = sum(overlap(box, pb) * 10 for pb in placed_boxes)
            score += sum(overlap(box, sc) * 5 for sc in station_circles)
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
            u, v = seq[i], seq[i+1]
            if u in STATIONS and v in STATIONS:
                adj[u].append((v, line))
                adj[v].append((u, line))
    return adj

def bfs_distances(target, adj):
    dist = {target: 0}
    q = deque([target])
    while q:
        curr = q.popleft()
        for neighbor, _ in adj[curr]:
            if neighbor not in dist:
                dist[neighbor] = dist[curr] + 1
                q.append(neighbor)
    return dist

def find_all_simple_paths(start, end, max_len, adj, cap=20000):
    dist_to_end = bfs_distances(end, adj)
    if start not in dist_to_end or dist_to_end[start] + 1 > max_len:
        return [], False
    results = []
    truncated = False

    def dfs(current, visited, visited_set):
        nonlocal truncated
        if len(results) >= cap:
            truncated = True
            return
        if len(visited) + dist_to_end.get(current, 999) > max_len:
            return
        if current == end:
            results.append(list(visited))
            return
        neighbors = sorted(set(n for n, _ in adj[current]), key=lambda x: dist_to_end.get(x, 999))
        for neighbor in neighbors:
            if neighbor not in visited_set:
                visited.append(neighbor)
                visited_set.add(neighbor)
                dfs(neighbor, visited, visited_set)
                visited_set.remove(neighbor)
                visited.pop()
                if truncated:
                    return

    dfs(start, [start], {start})
    return results, truncated

def get_line_sequence(path, adj):
    if len(path) < 2:
        return [[]]
    u0, u1 = path[0], path[1]
    init_lines = sorted(set(l for n, l in adj[u0] if n == u1))
    dp = {l: [[l]] for l in init_lines}

    for i in range(1, len(path) - 1):
        u, v = path[i], path[i+1]
        valid_lines = sorted(set(l for n, l in adj[u] if n == v))
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

def count_river_crossings(path):
    return sum(1 for i in range(len(path) - 1) if (path[i], path[i+1]) in HAN_RIVER_CROSSINGS)

def evaluate(path, clue, adj):
    c_type, val = clue[0], clue[1]
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
    elif c_type == "uses_line":
        seqs = get_line_sequence(path, adj)
        return any(val in s for s in seqs)
    return True

def get_matching(paths, clues, adj):
    return [p for p in paths if all(evaluate(p, c, adj) for c in clues)]

def is_minimal(paths_N, paths_ext, clues, adj):
    if len(clues) < 2:
        return False
    for i in range(len(clues)):
        sub = clues[:i] + clues[i+1:]
        if clues[i][0] == "total_stations":
            if len(get_matching(paths_ext, sub, adj)) <= 1:
                return False
        else:
            if len(get_matching(paths_N, sub, adj)) <= 1:
                return False
    return True

def clue_to_text(c_type, val):
    if c_type == "total_stations":
        return f"총 정차역 수는 출발/도착역 포함 정확히 {val}개 역이다."
    elif c_type == "transfer_count":
        return f"최소 환승 횟수는 정확히 {val}회이다."
    elif c_type == "river_crossings":
        return f"한강을 정확히 {val}번 건넜다."
    elif c_type == "via_station":
        return f"주요 거점인 '{val}역'을 반드시 경유했다."
    elif c_type == "avoid_station":
        return f"'{val}역'은 절대 거치지 않았다."
    elif c_type == "line_sequence":
        return f"탑승 노선 순서는 [{' ➔ '.join(val)}]이다."
    elif c_type == "uses_line":
        return f"경로 중 반드시 '{val}'을(를) 이용했다."
    return f"{c_type}: {val}"

gentle_spread(STATIONS)
optimize_labels(STATIONS)
adj = build_graph()

all_station_names = sorted(STATIONS.keys())
random.seed(777)

dist_map = {s: bfs_distances(s, adj) for s in all_station_names}
used_pairs = set()

metro_only = {f"{i}호선" for i in range(1, 10)}
special_lines = {"KTX", "ITX-청춘", "무궁화호", "GTX-A(북부)", "GTX-A(남부)", "서해선"}

def collect_tier(difficulty, count, min_l, max_l, mode="any", preferred_starts=None):
    results = []
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
        if (s, e) in used_pairs or (e, s) in used_pairs:
            continue

        d = dist_map[s].get(e, 999)
        pair_max_l = min(max_l, d + 4)
        all_paths_ext, trunc = find_all_simple_paths(s, e, pair_max_l + 3, adj, cap=20000)
        if trunc:
            all_paths_N, trunc_N = find_all_simple_paths(s, e, pair_max_l, adj, cap=20000)
            if trunc_N or len(all_paths_N) < 2:
                continue
            all_paths_ext = all_paths_N

        if len(all_paths_ext) < 3:
            continue

        cand_paths = [p for p in all_paths_ext if min_l <= len(p) <= pair_max_l]
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

            if mode == "metro_only":
                if not all(l in metro_only for l in line_seq) or p_transfers > 1:
                    continue
            elif mode == "require_special":
                if not any(l in special_lines for l in line_seq):
                    continue

            sec_pool = [("transfer_count", p_transfers), ("river_crossings", p_rc)]
            if len(line_seq) <= 3:
                sec_pool.append(("line_sequence", line_seq))
            for l in line_seq:
                if l in special_lines or l in {"신림선", "우이신설선", "공항철도", "신분당선"}:
                    sec_pool.append(("uses_line", l))
            for st in path[1:-1]:
                if len(STATIONS[st]["lines"]) > 1:
                    sec_pool.append(("via_station", st))
            for st in all_station_names:
                if st not in path and len(sec_pool) < 12:
                    if any(st in op for op in paths_N if op != path):
                        sec_pool.append(("avoid_station", st))

            found = False
            for k in [1, 2, 3]:
                if found:
                    break
                for sec_combo in combinations(sec_pool, k):
                    combo = [("total_stations", p_len)] + list(sec_combo)
                    matches = get_matching(paths_N, combo, adj)
                    if len(matches) == 1 and matches[0] == path:
                        if is_minimal(paths_N, all_paths_ext, combo, adj):
                            used_pairs.add((s, e))
                            clues_obj = [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in combo]
                            lvl = len(results) + 1
                            results.append({
                                "id": f"{difficulty}-{lvl}",
                                "difficulty": difficulty,
                                "level": lvl,
                                "title": f"{s} ➔ {e} ({difficulty} #{lvl})",
                                "story": f"{s}역에서 출발해 {e}역에 도착한 승객의 교통카드 기록입니다. 모든 단서를 충족하는 단 하나의 유일한 경로를 추리하세요.",
                                "start": s,
                                "end": e,
                                "path": path,
                                "path_length": p_len,
                                "transfers": p_transfers,
                                "lines": line_seq,
                                "clues": clues_obj,
                                "competing_paths": len(paths_N)
                            })
                            found = True
                            break
            if found:
                break

    print(f"★ [{difficulty}] Collected {len(results)} unique-OD stages!", flush=True)
    return results

special_stations = [
    n for n, st in STATIONS.items()
    if any(l in special_lines or l in {"경춘선", "수인분당선"} for l in st["lines"])
] + ["홍대입구", "여의도", "강남", "고속터미널", "사당", "시청", "동대문역사문화공원", "왕십리", "건대입구", "공덕"]

metro_stations = [n for n, st in STATIONS.items() if any(l in metro_only for l in st["lines"])]

master_stages = collect_tier("초고난이도", 50, 4, 8, mode="require_special", preferred_starts=list(set(special_stations)))
hard_stages = collect_tier("어려움", 50, 7, 10, mode="any")
medium_stages = collect_tier("중간", 50, 5, 7, mode="any")
easy_stages = collect_tier("쉬움", 50, 3, 5, mode="metro_only", preferred_starts=metro_stations)

all_stages = easy_stages + medium_stages + hard_stages + master_stages

dataset = {
    "line_colors": LINE_COLORS,
    "stations": STATIONS,
    "lines": LINES,
    "stages": all_stages
}

with open("scripts/full_game_data.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"\n★ GRAND TOTAL V2 STAGES: {len(all_stages)}", flush=True)
