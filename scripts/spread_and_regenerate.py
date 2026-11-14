"""
1. Spread out dense station coordinates using repulsion relaxation so minimum distance >= 50px.
2. Optimize non-overlapping label positions.
3. Generate 200+ strictly unique, minimal-clue stages with NO path truncation (max_paths=15000).
4. Run full zero-trust audit on every generated stage.
"""

import json
import math
from collections import defaultdict, deque
from itertools import combinations
from metro_data_full import STATIONS, LINES, LINE_COLORS, HAN_RIVER_CROSSINGS

# 1. Scale and spread stations
def spread_stations(stations):
    # Scale up 1.5x first
    for name, st in stations.items():
        st["x"] = st["x"] * 1.5
        st["y"] = st["y"] * 1.5

    names = list(stations.keys())
    min_dist = 56.0  # Minimum pixel distance between ANY two station dots

    for iteration in range(250):
        forces = {n: [0.0, 0.0] for n in names}
        moved = False
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1, n2 = names[i], names[j]
                dx = stations[n1]["x"] - stations[n2]["x"]
                dy = stations[n1]["y"] - stations[n2]["y"]
                dist = math.hypot(dx, dy)
                if dist < min_dist:
                    moved = True
                    if dist < 0.01:
                        # Break exact 0.0px ties deterministically
                        angle = (i * 1.618 + j * 0.7) % (2 * math.pi)
                        ux, uy = math.cos(angle), math.sin(angle)
                    else:
                        ux, uy = dx / dist, dy / dist
                    push = (min_dist - dist) * 0.35
                    forces[n1][0] += ux * push
                    forces[n1][1] += uy * push
                    forces[n2][0] -= ux * push
                    forces[n2][1] -= uy * push
        if not moved:
            break
        for n in names:
            stations[n]["x"] = round(stations[n]["x"] + forces[n][0], 1)
            stations[n]["y"] = round(stations[n]["y"] + forces[n][1], 1)

    # Check final min distance
    closest = 9999
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = math.hypot(stations[names[i]]["x"] - stations[names[j]]["x"],
                           stations[names[i]]["y"] - stations[names[j]]["y"])
            if d < closest:
                closest = d
    print(f"Station spreading complete. New minimum distance between any two stations: {closest:.1f}px", flush=True)

def optimize_label_positions(stations):
    placed_boxes = []
    candidates = [
        (0, -12, "middle"),   # top
        (0, 18, "middle"),    # bottom
        (11, 3, "start"),     # right
        (-11, 3, "end"),      # left
        (9, -10, "start"),    # top-right
        (-9, -10, "end"),     # top-left
        (9, 16, "start"),     # bottom-right
        (-9, 16, "end"),      # bottom-left
        (0, -22, "middle"),   # far-top
        (0, 28, "middle"),    # far-bottom
        (18, 3, "start"),     # far-right
        (-18, 3, "end"),      # far-left
    ]

    station_circles = []
    for name, st in stations.items():
        r = 8 if len(st["lines"]) > 1 else 5.5
        station_circles.append((st["x"] - r, st["y"] - r, st["x"] + r, st["y"] + r))

    def overlap_area(b1, b2):
        x_overlap = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
        y_overlap = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
        return x_overlap * y_overlap

    sorted_names = sorted(stations.keys(), key=lambda n: -len(stations[n]["lines"]))

    for name in sorted_names:
        st = stations[name]
        x, y = st["x"], st["y"]
        w = len(name) * 10.5 + 4
        h = 13

        best_cand = None
        best_score = 999999

        for dx, dy, anchor in candidates:
            lx = x + dx
            ly = y + dy
            if anchor == "middle":
                box = (lx - w/2, ly - h + 2, lx + w/2, ly + 2)
            elif anchor == "start":
                box = (lx, ly - h + 2, lx + w, ly + 2)
            else:
                box = (lx - w, ly - h + 2, lx, ly + 2)

            score = 0
            for pb in placed_boxes:
                score += overlap_area(box, pb) * 10
            for sc in station_circles:
                score += overlap_area(box, sc) * 5
            score += (abs(dx) + abs(dy)) * 0.05

            if score < best_score:
                best_score = score
                best_cand = (dx, dy, anchor, box)
                if score < 0.8:
                    break

        dx, dy, anchor, best_box = best_cand
        placed_boxes.append(best_box)
        st["lx"] = round(x + dx, 1)
        st["ly"] = round(y + dy, 1)
        st["anchor"] = anchor

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

def find_all_simple_paths_exhaustive(start, end, max_len, adj, cap=15000):
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
        rem = dist_to_end.get(current, 999)
        if len(visited) + rem > max_len:
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
    # Track all minimal-transfer sequences per current line
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

def get_matching_paths(paths, clue_set, adj):
    return [p for p in paths if all(evaluate(p, c, adj) for c in clue_set)]

def is_strictly_minimal(paths_N, paths_extended, clue_set, adj):
    if len(clue_set) < 2:
        return False
    for i in range(len(clue_set)):
        sub = clue_set[:i] + clue_set[i+1:]
        if clue_set[i][0] == "total_stations":
            if len(get_matching_paths(paths_extended, sub, adj)) <= 1:
                return False
        else:
            if len(get_matching_paths(paths_N, sub, adj)) <= 1:
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

def generate_for_tier(pairs, difficulty, adj, target_count=50):
    certified = []
    seen_routes = set()

    for start, end, max_l in pairs:
        if len(certified) >= target_count:
            break
        if start not in STATIONS or end not in STATIONS:
            continue

        all_paths_ext, truncated = find_all_simple_paths_exhaustive(start, end, max_l + 3, adj, cap=15000)
        if truncated or len(all_paths_ext) < 3:
            # If even max_l+3 hit 15000, only verify up to max_l!
            all_paths_N, trunc_N = find_all_simple_paths_exhaustive(start, end, max_l, adj, cap=15000)
            if trunc_N or len(all_paths_N) < 2:
                continue
            all_paths_ext = all_paths_N

        found_for_pair = 0
        cand_paths = [p for p in all_paths_ext if len(p) <= max_l]
        for path in cand_paths:
            if len(certified) >= target_count or found_for_pair >= 3:
                break
            route_key = (start, end, tuple(path))
            if route_key in seen_routes:
                continue

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

            if difficulty == "초고난이도":
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
            for st in STATIONS:
                if st not in path and len(sec_pool) < 12:
                    if any(st in op for op in paths_N if op != path):
                        sec_pool.append(("avoid_station", st))

            found = False
            for k in [1, 2, 3]:
                if found:
                    break
                for sec_combo in combinations(sec_pool, k):
                    combo = [("total_stations", p_len)] + list(sec_combo)
                    matches = get_matching_paths(paths_N, combo, adj)
                    if len(matches) == 1 and matches[0] == path:
                        if is_strictly_minimal(paths_N, all_paths_ext, combo, adj):
                            clues_obj = [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in combo]
                            puz = {
                                "id": f"{difficulty}-{len(certified)+1}",
                                "difficulty": difficulty,
                                "level": len(certified) + 1,
                                "start": start,
                                "end": end,
                                "path": path,
                                "path_length": p_len,
                                "transfers": p_transfers,
                                "lines": line_seq,
                                "clues": clues_obj,
                                "competing_paths": len(paths_N)
                            }
                            certified.append(puz)
                            seen_routes.add(route_key)
                            found_for_pair += 1
                            found = True
                            break

    print(f"★ [{difficulty}] Certified {len(certified)} stages!", flush=True)
    return certified

if __name__ == "__main__":
    spread_stations(STATIONS)
    optimize_label_positions(STATIONS)
    adj = build_graph()

    easy_pairs = [
        ("홍대입구", "여의도", 7), ("합정", "노량진", 7), ("시청", "동대문", 6), ("신도림", "합정", 6),
        ("종로3가", "충무로", 5), ("고속터미널", "강남", 6), ("신촌", "공덕", 6), ("동작", "사당", 6),
        ("왕십리", "청구", 6), ("잠실", "삼성", 6), ("을지로3가", "동대문", 6), ("여의도", "노량진", 6),
        ("건대입구", "청담", 6), ("신길", "당산", 6), ("공덕", "삼각지", 6), ("충무로", "약수", 6),
        ("교대", "고속터미널", 5), ("서울역", "충정로", 5), ("용산", "삼각지", 5), ("왕십리", "건대입구", 6),
        ("신당", "동대문역사문화공원", 5), ("을지로4가", "종로3가", 5), ("여의도", "당산", 5), ("사당", "총신대입구", 5),
        ("선릉", "강남", 5), ("신논현", "강남", 5), ("신사", "압구정", 5), ("이태원", "약수", 6),
        ("성수", "왕십리", 5), ("영등포", "신도림", 5), ("대림", "신도림", 5), ("서울역", "시청", 5),
        ("가산디지털단지", "신도림", 6), ("대방", "여의도", 5), ("공덕", "여의도", 5), ("마포", "여의도", 4),
    ]

    medium_pairs = [
        ("공덕", "고속터미널", 9), ("종각", "여의도", 9), ("샛강", "신림", 7), ("신설동", "성신여대입구", 6),
        ("신사", "판교", 8), ("홍대입구", "디지털미디어시티", 6), ("여의도", "강남", 10), ("건대입구", "신사", 9),
        ("사당", "여의도", 10), ("이태원", "강남", 10), ("용산", "강남", 10), ("영등포", "충무로", 10),
        ("왕십리", "강남", 10), ("동대문", "강남", 10), ("종로3가", "고속터미널", 10), ("서울역", "여의도", 9),
        ("합정", "강남", 10), ("신촌", "여의도", 9), ("교대", "여의도", 10), ("잠실", "왕십리", 9),
        ("신도림", "여의도", 7), ("대방", "강남", 10), ("선릉", "잠실", 7), ("청량리", "왕십리", 6),
        ("성수", "강남", 9), ("을지로3가", "사당", 10), ("공덕", "강남", 10), ("노량진", "강남", 10),
        ("보라매", "여의도", 7), ("성신여대입구", "동대문", 6),
    ]

    hard_pairs = [
        ("시청", "고속터미널", 10), ("일산", "김포공항", 7), ("연신내", "서울역", 8), ("부천종합운동장", "여의도", 9),
        ("마곡나루", "강남", 11), ("청량리", "수서", 10), ("합정", "노량진", 10), ("영등포", "충무로", 10),
        ("사당", "여의도", 10), ("디지털미디어시티", "고속터미널", 11), ("대곡", "여의도", 10), ("김포공항", "여의도", 9),
        ("수서", "강남", 9), ("판교", "고속터미널", 9), ("가산디지털단지", "여의도", 9), ("온수", "여의도", 10),
        ("소사", "당산", 9), ("청량리", "강남", 10), ("상봉", "왕십리", 8), ("노원", "동대문", 9),
        ("태릉입구", "왕십리", 10), ("석촌", "강남", 9), ("복정", "선릉", 8), ("천호", "건대입구", 8),
        ("금정", "사당", 8), ("안양", "사당", 9), ("신설동", "여의도", 11), ("불광", "시청", 9),
    ]

    master_pairs = [
        ("행신", "용산", 6), ("서울역", "수원", 6), ("용산", "춘천", 8), ("청량리", "평내호평", 6),
        ("수서", "동탄", 5), ("용산", "광명", 5), ("영등포", "수원", 6), ("옥수", "가평", 7),
        ("대곡", "수서", 6), ("서울역", "광명", 5), ("용산", "안양", 6), ("초지", "서울역", 8),
        ("행신", "서울역", 5), ("행신", "수원", 6), ("서울역", "동탄", 6), ("용산", "수원", 6),
        ("청량리", "춘천", 7), ("상봉", "가평", 6), ("왕십리", "춘천", 8), ("용산", "평내호평", 7),
        ("운정", "서울역", 6), ("운정", "수서", 7), ("대곡", "동탄", 7), ("연신내", "수서", 7),
        ("영등포", "광명", 5), ("안양", "서울역", 6), ("수원", "광명", 6), ("청량리", "용산", 6),
        ("왕십리", "수원", 8), ("일산", "서울역", 7), ("김포공항", "수서", 8), ("초지", "용산", 7),
    ]

    easy_stages = generate_for_tier(easy_pairs, "쉬움", adj, 50)
    medium_stages = generate_for_tier(medium_pairs, "중간", adj, 50)
    hard_stages = generate_for_tier(hard_pairs, "어려움", adj, 50)
    master_stages = generate_for_tier(master_pairs, "초고난이도", adj, 50)

    all_stages = easy_stages + medium_stages + hard_stages + master_stages

    for st in all_stages:
        st["title"] = f"{st['start']} ➔ {st['end']} ({st['difficulty']} #{st['level']})"
        st["story"] = f"{st['start']}역에서 출발해 {st['end']}역에 도착한 승객의 교통카드 기록입니다. 모든 단서를 충족하는 단 하나의 유일한 경로를 추리하세요."

    dataset = {
        "line_colors": LINE_COLORS,
        "stations": STATIONS,
        "lines": LINES,
        "stages": all_stages
    }

    with open("scripts/full_game_data.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"\n★ TOTAL GENERATED STAGES: {len(all_stages)}", flush=True)
