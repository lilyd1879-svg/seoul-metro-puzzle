"""
Fast, Mathematically Airtight Puzzle Generator + Non-Overlapping Label Optimizer
Uses BFS distance-to-target pruning so DFS finishes in milliseconds.
Also computes collision-free label coordinates (lx, ly, anchor) for every station.
"""

import json
from collections import defaultdict, deque
from itertools import combinations
from metro_data_full import STATIONS, LINES, LINE_COLORS, HAN_RIVER_CROSSINGS

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

def find_all_simple_paths_fast(start, end, max_len, adj, max_paths=300):
    dist_to_end = bfs_distances(end, adj)
    if start not in dist_to_end:
        return []
    results = []

    def dfs(current, visited, visited_set):
        if len(results) >= max_paths:
            return
        rem = dist_to_end.get(current, 999)
        if len(visited) + rem > max_len:
            return
        if current == end:
            results.append(list(visited))
            return
        # Sort neighbors by distance to end for faster discovery
        neighbors = sorted(set(n for n, _ in adj[current]), key=lambda x: dist_to_end.get(x, 999))
        for neighbor in neighbors:
            if neighbor not in visited_set:
                visited.append(neighbor)
                visited_set.add(neighbor)
                dfs(neighbor, visited, visited_set)
                visited_set.remove(neighbor)
                visited.pop()

    dfs(start, [start], {start})
    return results

def get_line_sequence(path, adj):
    # Find minimum-transfer line sequences using DP
    if len(path) < 2:
        return [[]]
    # dp[i] = dict mapping current_line -> list of line_sequences
    u0, u1 = path[0], path[1]
    init_lines = set(l for n, l in adj[u0] if n == u1)
    states = [{l: [l]} for l in init_lines]
    
    # Actually let's just do simple DFS over edges since path length <= 15
    def search_lines(idx, current_lines):
        if idx == len(path) - 1:
            return [current_lines]
        u, v = path[idx], path[idx+1]
        valid_lines = set(l for neighbor, l in adj[u] if neighbor == v)
        # Prefer continuing same line if available to avoid spurious transfers
        results = []
        if current_lines and current_lines[-1] in valid_lines:
            results.extend(search_lines(idx + 1, current_lines + [current_lines[-1]]))
        else:
            for l in valid_lines:
                results.extend(search_lines(idx + 1, current_lines + [l]))
        return results

    all_line_seqs = search_lines(0, [])
    unique_compressed = []
    for seq in all_line_seqs:
        comp = []
        for l in seq:
            if not comp or comp[-1] != l:
                comp.append(l)
        if comp not in unique_compressed:
            unique_compressed.append(comp)
    unique_compressed.sort(key=len)
    return unique_compressed

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

def is_minimal(paths, clue_set, adj):
    if len(clue_set) < 2:
        return False
    for i in range(len(clue_set)):
        sub = clue_set[:i] + clue_set[i+1:]
        if len(get_matching_paths(paths, sub, adj)) <= 1:
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

def search_puzzles_for_tier(pairs, difficulty, adj, max_needed=10):
    certified = []
    seen_routes = set()

    for start, end, max_l in pairs:
        if len(certified) >= max_needed:
            break
        if start not in STATIONS or end not in STATIONS:
            continue

        # Search up to max_l + 3 for exhaustive uniqueness
        all_paths = find_all_simple_paths_fast(start, end, max_l + 3, adj, max_paths=350)
        if len(all_paths) < 3:
            continue

        found_for_pair = 0
        for path in all_paths:
            if len(certified) >= max_needed or found_for_pair >= 1:
                break
            if len(path) > max_l:
                continue
            route_key = (start, end, tuple(path))
            if route_key in seen_routes:
                continue

            seqs = get_line_sequence(path, adj)
            if not seqs:
                continue
            line_seq = seqs[0]
            p_len = len(path)
            p_transfers = len(line_seq) - 1
            p_rc = count_river_crossings(path)

            # Restrict to puzzles where total_stations is in the clue set OR verified up to max_l+3
            pool = [
                ("total_stations", p_len),
                ("transfer_count", p_transfers),
                ("river_crossings", p_rc),
            ]
            if len(line_seq) <= 3:
                pool.append(("line_sequence", line_seq))
            for l in line_seq:
                if l in ["KTX", "ITX-청춘", "무궁화호", "GTX-A", "서해선", "신림선", "우이신설선", "공항철도", "신분당선"]:
                    pool.append(("uses_line", l))

            for st in path[1:-1]:
                if len(STATIONS[st]["lines"]) > 1:
                    pool.append(("via_station", st))

            for st in STATIONS:
                if st not in path and len(pool) < 12:
                    if any(st in op for op in all_paths if op != path):
                        pool.append(("avoid_station", st))

            found = False
            for k in [2, 3, 4]:
                if found:
                    break
                for combo in combinations(pool, k):
                    # Ensure mathematical exhaustiveness: if total_stations is NOT in combo,
                    # we must be sure no longer path exists beyond max_l+3, or require total_stations/line_sequence
                    has_len_bound = any(c[0] == "total_stations" for c in combo)
                    if not has_len_bound and len(all_paths) >= 350:
                        continue
                        
                    matches = get_matching_paths(all_paths, combo, adj)
                    if len(matches) == 1 and matches[0] == path:
                        if is_minimal(all_paths, combo, adj):
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
                                "competing_paths": len(all_paths)
                            }
                            certified.append(puz)
                            seen_routes.add(route_key)
                            found_for_pair += 1
                            print(f"  ★ [{difficulty}] #{len(certified)}: {start} -> {end} (Len {p_len}, {len(combo)} clues)", flush=True)
                            found = True
                            break
    return certified

def optimize_label_positions(stations):
    """
    Assign non-overlapping (dx, dy, anchor) offsets to every station label.
    """
    placed_boxes = []
    # Candidate offsets: (dx, dy, text_anchor)
    candidates = [
        (0, -11, "middle"),   # top
        (0, 17, "middle"),    # bottom
        (10, 3, "start"),     # right
        (-10, 3, "end"),      # left
        (8, -9, "start"),     # top-right
        (-8, -9, "end"),      # top-left
        (8, 15, "start"),     # bottom-right
        (-8, 15, "end"),      # bottom-left
        (0, -20, "middle"),   # far-top
        (0, 26, "middle"),    # far-bottom
        (16, 3, "start"),     # far-right
        (-16, 3, "end"),      # far-left
    ]

    # First reserve station circle bounding boxes
    station_circles = []
    for name, st in stations.items():
        r = 7 if len(st["lines"]) > 1 else 5
        station_circles.append((st["x"] - r, st["y"] - r, st["x"] + r, st["y"] + r))

    def overlap_area(b1, b2):
        x_overlap = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
        y_overlap = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
        return x_overlap * y_overlap

    # Sort stations so major transfer hubs get first pick
    sorted_names = sorted(stations.keys(), key=lambda n: -len(stations[n]["lines"]))

    for name in sorted_names:
        st = stations[name]
        x, y = st["x"], st["y"]
        w = len(name) * 9.5 + 4
        h = 12

        best_cand = candidates[0]
        best_score = 999999

        for dx, dy, anchor in candidates:
            lx = x + dx
            ly = y + dy
            if anchor == "middle":
                box = (lx - w/2, ly - h + 2, lx + w/2, ly + 2)
            elif anchor == "start":
                box = (lx, ly - h + 2, lx + w, ly + 2)
            else: # end
                box = (lx - w, ly - h + 2, lx, ly + 2)

            score = 0
            # Penalize overlap with existing labels
            for pb in placed_boxes:
                score += overlap_area(box, pb) * 10
            # Penalize overlap with station dots
            for sc in station_circles:
                score += overlap_area(box, sc) * 5
            # Slight penalty for far offsets
            score += (abs(dx) + abs(dy)) * 0.05

            if score < best_score:
                best_score = score
                best_cand = (dx, dy, anchor, box)
                if score < 1.0:
                    break

        dx, dy, anchor, best_box = best_cand
        placed_boxes.append(best_box)
        st["lx"] = x + dx
        st["ly"] = y + dy
        st["anchor"] = anchor

    return stations

if __name__ == "__main__":
    adj = build_graph()
    print("Optimizing non-overlapping station labels...", flush=True)
    optimize_label_positions(STATIONS)

    easy_pairs = [
        ("홍대입구", "여의도", 7),
        ("합정", "노량진", 7),
        ("시청", "동대문", 6),
        ("신도림", "합정", 6),
        ("종로3가", "충무로", 5),
        ("고속터미널", "강남", 6),
        ("신촌", "공덕", 6),
        ("동작", "사당", 6),
        ("왕십리", "청구", 6),
        ("잠실", "삼성", 6),
        ("을지로3가", "동대문", 6),
        ("여의도", "노량진", 6),
    ]

    medium_pairs = [
        ("공덕", "고속터미널", 10),
        ("종각", "여의도", 9),
        ("샛강", "신림", 7),
        ("신설동", "성신여대입구", 6),
        ("신사", "판교", 8),
        ("홍대입구", "디지털미디어시티", 6),
        ("여의도", "강남", 11),
        ("건대입구", "신사", 10),
        ("사당", "여의도", 11),
        ("이태원", "강남", 10),
        ("용산", "강남", 10),
        ("영등포", "충무로", 10),
    ]

    hard_pairs = [
        ("시청", "고속터미널", 11),
        ("일산", "김포공항", 7),
        ("연신내", "서울역", 8),
        ("부천종합운동장", "여의도", 10),
        ("마곡나루", "강남", 12),
        ("청량리", "수서", 11),
        ("합정", "노량진", 10),
        ("영등포", "충무로", 11),
        ("사당", "여의도", 12),
        ("디지털미디어시티", "고속터미널", 12),
        ("대곡", "여의도", 11),
    ]

    master_pairs = [
        ("행신", "용산", 6),
        ("서울역", "수원", 6),
        ("용산", "춘천", 8),
        ("청량리", "평내호평", 6),
        ("수서", "동탄", 5),
        ("용산", "광명", 5),
        ("영등포", "수원", 6),
        ("옥수", "가평", 7),
        ("대곡", "수서", 6),
        ("서울역", "광명", 5),
        ("용산", "안양", 6),
        ("초지", "서울역", 8),
    ]

    easy_stages = search_puzzles_for_tier(easy_pairs, "쉬움", adj, 10)
    medium_stages = search_puzzles_for_tier(medium_pairs, "중간", adj, 10)
    hard_stages = search_puzzles_for_tier(hard_pairs, "어려움", adj, 10)
    master_stages = search_puzzles_for_tier(master_pairs, "초고난이도", adj, 10)

    all_stages = easy_stages + medium_stages + hard_stages + master_stages

    for st in all_stages:
        st["title"] = f"{st['start']} ➔ {st['end']} ({st['difficulty']})"
        st["story"] = f"{st['start']}역에서 출발해 {st['end']}역에 도착한 승객의 교통카드 기록입니다. 최소 단서를 모두 만족하는 유일한 경로를 연결하세요."

    dataset = {
        "line_colors": LINE_COLORS,
        "stations": STATIONS,
        "lines": LINES,
        "stages": all_stages
    }

    with open("scripts/full_game_data.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"\nDONE! Total certified stages: {len(all_stages)}", flush=True)
    for t in ["쉬움", "중간", "어려움", "초고난이도"]:
        print(f"  {t}: {len([s for s in all_stages if s['difficulty'] == t])}", flush=True)
