"""
Massive Puzzle Generator and Verifier for Full Metropolitan Network
Generates dozens of certified minimal unique puzzles across:
- 쉬움 (Easy)
- 중간 (Medium)
- 어려움 (Hard)
- 초고난이도 (Master: KTX / ITX-청춘 / 무궁화호 / GTX-A / 서해선)
"""

import json
from collections import defaultdict
from itertools import combinations
from metro_data_full import STATIONS, LINES, LINE_COLORS, HAN_RIVER_CROSSINGS

def build_graph(allowed_lines=None):
    adj = defaultdict(list)
    for line, seq in LINES.items():
        if allowed_lines and line not in allowed_lines:
            continue
        for i in range(len(seq) - 1):
            u, v = seq[i], seq[i+1]
            if u in STATIONS and v in STATIONS:
                adj[u].append((v, line))
                adj[v].append((u, line))
    return adj

def get_line_sequence(path, adj):
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

def find_all_simple_paths(start, end, max_len, adj):
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
    matches = []
    for p in paths:
        if all(evaluate(p, c, adj) for c in clue_set):
            matches.append(p)
    return matches

def is_minimal(paths, clue_set, adj):
    if len(clue_set) < 2:
        return False
    for i in range(len(clue_set)):
        sub_clues = clue_set[:i] + clue_set[i+1:]
        sub_matches = get_matching_paths(paths, sub_clues, adj)
        if len(sub_matches) <= 1:
            return False
    return True

def clue_to_text(c_type, val):
    if c_type == "total_stations":
        return f"총 정차역 수는 출발/도착역 포함 정확히 {val}개 역이다."
    elif c_type == "transfer_count":
        return f"환승은 정확히 {val}회 발생했다."
    elif c_type == "river_crossings":
        return f"한강을 정확히 {val}번 건넜다."
    elif c_type == "via_station":
        return f"주요 거점인 '{val}역'을 경유했다."
    elif c_type == "avoid_station":
        return f"우회를 위해 '{val}역'은 거치지 않았다."
    elif c_type == "line_sequence":
        return f"탑승한 노선 순서는 [{' ➔ '.join(val)}]이다."
    elif c_type == "uses_line":
        return f"경로 중 반드시 '{val}'에 탑승했다."
    return f"{c_type}: {val}"

def search_puzzles_for_tier(pairs, difficulty, adj, max_needed=10):
    certified = []
    seen_routes = set()

    for start, end, max_l in pairs:
        if len(certified) >= max_needed:
            break
        if start not in STATIONS or end not in STATIONS:
            continue
            
        all_paths = find_all_simple_paths(start, end, max_l, adj)
        if len(all_paths) < 2 or len(all_paths) > 200:
            continue
            
        print(f"[{difficulty}] Searching {start} -> {end} ({len(all_paths)} paths)...")
        
        for path in all_paths:
            if len(certified) >= max_needed:
                break
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

            # Build candidate clue pool
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
                if st not in path and len(pool) < 14:
                    if any(st in op for op in all_paths if op != path):
                        pool.append(("avoid_station", st))

            # Test subsets of size 2, 3, 4
            found_for_path = False
            for k in [2, 3, 4]:
                if found_for_path:
                    break
                for combo in combinations(pool, k):
                    matches = get_matching_paths(all_paths, combo, adj)
                    if len(matches) == 1 and matches[0] == path:
                        if is_minimal(all_paths, combo, adj):
                            clues_obj = [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in combo]
                            puz = {
                                "id": f"{difficulty.lower()}-{len(certified)+1}",
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
                            print(f"  ★ CERTIFIED [{difficulty}] #{len(certified)}: {start} -> {end} (Len {p_len})")
                            found_for_path = True
                            break

    return certified

# Define candidate pairs for each difficulty tier
full_adj = build_graph()

# 1. Easy pairs (Metro 1-9 short distances)
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
    ("건대입구", "청담", 6),
    ("신길", "당산", 6),
    ("공덕", "삼각지", 6),
]

# 2. Medium pairs (1~2 transfers, river crossings, light rails / Shinbundang)
medium_pairs = [
    ("공덕", "고속터미널", 10),
    ("종각", "여의도", 10),
    ("샛강", "신림", 7),          # 신림선
    ("신설동", "성신여대입구", 6),   # 우이신설선
    ("신사", "판교", 9),           # 신분당선
    ("홍대입구", "디지털미디어시티", 6), # 경의중앙/공항철도
    ("여의도", "강남", 11),
    ("건대입구", "신사", 10),
    ("사당", "여의도", 11),
    ("이태원", "강남", 10),
    ("용산", "강남", 11),
    ("당산", "신사", 11),
    ("영등포", "충무로", 10),
    ("왕십리", "강남", 11),
    ("동대문", "강남", 11),
]

# 3. Hard pairs (2~3 transfers, Seohae line, GTX-A, dense network)
hard_pairs = [
    ("시청", "고속터미널", 11),
    ("일산", "김포공항", 8),       # 서해선 / 경의중앙선
    ("연신내", "서울역", 8),       # GTX-A / 3호선 / 6호선
    ("부천종합운동장", "여의도", 11), # 서해선 / 7호선 / 9호선
    ("마곡나루", "강남", 13),      # 공항철도 / 9호선 / 2호선
    ("청량리", "수서", 12),        # 수인분당선 / 3호선
    ("합정", "노량진", 11),        # 도심 우회
    ("영등포", "충무로", 11),
    ("사당", "여의도", 12),
    ("디지털미디어시티", "고속터미널", 13),
    ("상봉", "강남", 13),
    ("수원", "사당", 13),
    ("대곡", "여의도", 12),
    ("김포공항", "강남", 14),
]

# 4. Master pairs (KTX, ITX-청춘, 무궁화호, GTX-A 대도약)
master_pairs = [
    ("행신", "용산", 7),          # KTX vs 경의중앙선
    ("서울역", "수원", 6),         # KTX vs 무궁화호 vs 1호선
    ("용산", "춘천", 8),          # ITX-청춘 vs 경춘선
    ("청량리", "평내호평", 6),      # ITX-청춘 vs 경춘선
    ("수서", "동탄", 5),          # GTX-A vs KTX(SRT)
    ("용산", "광명", 5),          # KTX 직통 vs 1호선 환승
    ("영등포", "수원", 6),         # KTX / 무궁화호 vs 1호선
    ("옥수", "가평", 7),          # ITX-청춘
    ("대곡", "수서", 7),          # GTX-A 급행 연계
    ("서울역", "광명", 5),         # KTX 급행
    ("용산", "안양", 6),          # 무궁화호 급행
    ("초지", "서울역", 8),         # KTX / 서해선 / 4호선
]

print("=== GENERATING EASY STAGES ===")
easy_stages = search_puzzles_for_tier(easy_pairs, "쉬움", full_adj, max_needed=10)

print("\n=== GENERATING MEDIUM STAGES ===")
medium_stages = search_puzzles_for_tier(medium_pairs, "중간", full_adj, max_needed=10)

print("\n=== GENERATING HARD STAGES ===")
hard_stages = search_puzzles_for_tier(hard_pairs, "어려움", full_adj, max_needed=10)

print("\n=== GENERATING MASTER STAGES ===")
master_stages = search_puzzles_for_tier(master_pairs, "초고난이도", full_adj, max_needed=10)

all_generated_stages = easy_stages + medium_stages + hard_stages + master_stages

# Add descriptive titles and stories
stage_titles = {
    "쉬움": [
        ("홍대에서 여의도: 9호선 지름길", "퇴근길, 한강을 빠르게 건너 여의도 금융가로 향하는 승객의 최소 단서 경로."),
        ("수산시장 특급", "합정에서 노량진까지 9호선 급행을 이용한 최단 환승 경로입니다."),
        ("도심 관통선", "시청에서 동대문 패션타운으로 향하는 지하철 1호선의 기본 이동 경로."),
        ("서남권 순환", "신도림에서 합정까지 2호선 서남부 축을 순환하는 승객의 경로."),
        ("종로-충무로 링크", "종로3가에서 충무로 영화의 거리로 향하는 3호선의 알짜 경로."),
        ("강남 중심축 이동", "고속터미널에서 강남역까지 서초 권역을 이동하는 지하철 루트."),
        ("마포-신촌 라인", "신촌 대학가에서 공덕 행정타운으로 이동하는 승객의 경로."),
        ("동작-사당 남부선", "동작에서 사당으로 향하는 4호선 직행 경로."),
        ("동대문-성동 연결선", "왕십리에서 청구로 이어지는 5호선 구간."),
        ("잠실-삼성 비즈니스 라인", "잠실 롯데월드타워에서 코엑스 삼성역으로 향하는 2호선 경로.")
    ],
    "중간": [
        ("동작대교와 강남 터미널", "공덕에서 동작대교를 건너 고속터미널로 향한 승객의 2회 환승 경로."),
        ("도심 탈출: 종각-여의도", "종각역에서 1호선을 타고 도심을 빠져나와 여의도로 향한 직장인."),
        ("신림선 샛강 쾌속선", "샛강역에서 신림선 경전철을 타고 관악산 방면으로 향한 통근길."),
        ("우이신설선 북부 탐방", "신설동에서 성신여대로 이어지는 북부 경전철 네트워크 경로."),
        ("신분당선 판교 테크노밸리행", "신사역에서 출발하여 판교 IT밸리로 초고속 이동한 IT 직장인."),
        ("공항철도 마포 횡단", "홍대입구에서 DMC 디지털미디어시티로 향하는 광역 환승망."),
        ("여의도-강남 횡단축", "여의도 금융가에서 테헤란로 강남역으로 향하는 직장인의 유일 경로."),
        ("성동-강남 횡단", "건대입구에서 영동대교를 건너 신사역으로 향하는 복합 경로."),
        ("사당-여의도 남서부 링", "사당역에서 노량진 축을 타고 여의도로 진입한 승객의 경로."),
        ("이태원-강남 야간선", "이태원에서 한강을 건너 강남역으로 이동한 심야 이동 경로.")
    ],
    "어려움": [
        ("서울 남북 종단: 7호선의 트릭", "시청역에서 출발하여 9호선 대신 7호선 총신대입구를 거쳐간 고난도 경로."),
        ("서해선 한강하저 터널", "일산에서 서해선을 타고 한강 밑을 뚫어 김포공항에 도착한 승객."),
        ("GTX-A 도심 급행선", "연신내에서 서울역까지 지하 50m GTX-A 급행을 이용한 초고속 이동."),
        ("부천-여의도 광역 네트워크", "부천종합운동장에서 7호선/서해선을 거쳐 여의도로 진입한 광역 통근길."),
        ("마곡-강남 골드라인", "마곡나루에서 출발해 9호선/2호선을 절묘하게 갈아탄 강남행 여정."),
        ("청량리-수서 동남부 대각선", "청량리에서 수서역까지 수인분당선을 축으로 횡단한 장거리 경로."),
        ("도심 대우회 미스터리", "합정에서 노량진까지 도심을 크게 돌아 이동한 의문의 우회 루트."),
        ("충무로 심야 영화제행", "영등포에서 중심가 시청과 여의도를 모두 피해 충무로로 들어간 야간 승객."),
        ("사당-여의도 복합 환승망", "사당에서 출발하여 4호선-9호선-1호선이 얽힌 복합 경로."),
        ("DMC-고속터미널 광역 축", "디지털미디어시티에서 강남 터미널로 향하는 고난도 광역 이동 경로.")
    ],
    "초고난이도": [
        ("KTX 수도권 급행 도약: 행신-용산", "행신역에서 일반 전철이 아닌 KTX 고속열차를 타고 용산역에 단숨에 도착한 승객!"),
        ("경부선 KTX-무궁화호 트릭: 서울-수원", "서울역에서 수원역까지 수많은 전철역을 건너뛰고 간선열차로 워프한 초특급 경로."),
        ("ITX-청춘 호반열차: 용산-춘천", "용산에서 춘천까지 북한강을 따라 질주하는 2층 열차 ITX-청춘의 쾌속 경로."),
        ("경춘선 청량리 급행 스킵", "청량리에서 평내호평까지 완행 전철을 제치고 ITX-청춘으로 도약한 승객."),
        ("수서-동탄 GTX 고속철도망", "수서역에서 동탄신도시까지 KTX 선로를 공용하는 GTX-A의 초고속 이동."),
        ("KTX 한강철교 건너기: 용산-광명", "용산역에서 광명역까지 한강을 건너 전철 15개 역을 스킵한 KTX 특급 경로."),
        ("영등포-수원 일반열차 바이트", "영등포역에서 무궁화호를 탑승해 경기 남부 중심 수원역으로 도약한 경로."),
        ("옥수-가평 호반 급행선", "옥수역에서 ITX-청춘에 탑승하여 청평/가평으로 향한 여행객의 유일 경로."),
        ("대곡-수서 GTX-A 관통선", "대곡역에서 수서역까지 수도권 서북부와 동남부를 잇는 GTX-A 연계 이동."),
        ("서울-광명 KTX 초단축 경로", "서울역에서 광명역까지 시내 전철 환승을 모두 무력화하는 KTX 직행 경로.")
    ]
}

for tier, stages in [("쉬움", easy_stages), ("중간", medium_stages), ("어려움", hard_stages), ("초고난이도", master_stages)]:
    for i, st in enumerate(stages):
        if i < len(stage_titles[tier]):
            st["title"] = stage_titles[tier][i][0]
            st["story"] = stage_titles[tier][i][1]
        else:
            st["title"] = f"{st['start']} ➔ {st['end']} 경로 복원"
            st["story"] = f"{st['start']}에서 {st['end']}까지 이동한 승객의 최소 단서 유일 경로를 찾으세요."

final_massive_dataset = {
    "line_colors": LINE_COLORS,
    "stations": STATIONS,
    "lines": LINES,
    "stages": all_generated_stages
}

with open("scripts/full_game_data.json", "w", encoding="utf-8") as f:
    json.dump(final_massive_dataset, f, ensure_ascii=False, indent=2)

print(f"\n★ TOTAL CERTIFIED STAGES GENERATED: {len(all_generated_stages)}")
for tier in ["쉬움", "중간", "어려움", "초고난이도"]:
    cnt = len([s for s in all_generated_stages if s["difficulty"] == tier])
    print(f"  - {tier}: {cnt}개 스테이지")
