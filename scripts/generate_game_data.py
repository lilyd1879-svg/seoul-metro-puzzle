"""
Generate complete game dataset for web app:
- Stations (id, name, x, y, lines, area)
- Lines (name, color, station sequence)
- Verified Puzzle Stages across Easy, Medium, Hard
"""

import json
from metro_data import STATIONS, LINES, LINE_COLORS, HAN_RIVER_CROSSINGS
from verify_puzzles import build_graph, find_all_simple_paths, get_line_sequence, count_river_crossings

adj = build_graph()

# Select verified curated stages
curated_stages = [
    # EASY 1
    {
        "id": "easy-1",
        "difficulty": "쉬움",
        "level": 1,
        "title": "첫 번째 퇴근길: 홍대에서 여의도까지",
        "story": "퇴근 시간, 한강을 건너 여의도로 향하는 급행 승객의 가장 깔끔한 경로를 찾으세요.",
        "start": "홍대입구",
        "end": "여의도",
        "solution": ["홍대입구", "합정", "당산", "국회의사당", "여의도"],
        "lines": ["2호선", "9호선"],
        "clues": [
            {"type": "total_stations", "text": "총 정차역 수는 출발/도착 포함 정확히 5개 역이다.", "val": 5},
            {"type": "via_station", "text": "9호선 환승역인 '당산역'을 경유했다.", "val": "당산"},
            {"type": "avoid_station", "text": "5호선 환승역인 '영등포구청역'은 거치지 않았다.", "val": "영등포구청"}
        ]
    },
    # EASY 2
    {
        "id": "easy-2",
        "difficulty": "쉬움",
        "level": 2,
        "title": "노량진 수산시장 급행",
        "story": "합정에서 노량진으로 이동한 승객. 9호선 급행 라인을 이용한 최단 경로입니다.",
        "start": "합정",
        "end": "노량진",
        "solution": ["합정", "당산", "국회의사당", "여의도", "샛강", "노량진"],
        "lines": ["2호선", "9호선"],
        "clues": [
            {"type": "total_stations", "text": "총 정차역 수는 출발/도착 포함 정확히 6개 역이다.", "val": 6},
            {"type": "transfer_count", "text": "환승은 단 1회만 발생했다 (2호선 ➔ 9호선).", "val": 1},
            {"type": "river_crossings", "text": "한강을 정확히 1번 건넜다 (당산철교).", "val": 1}
        ]
    },
    # MEDIUM 1
    {
        "id": "medium-1",
        "difficulty": "중간",
        "level": 1,
        "title": "강남 터미널의 비밀",
        "story": "공덕에서 고속터미널까지 이동한 승객. 6호선에서 시작해 4호선을 거쳐 9호선으로 환승했습니다.",
        "start": "공덕",
        "end": "고속터미널",
        "solution": ["공덕", "효창공원앞", "삼각지", "신용산", "이촌", "동작", "구반포", "신반포", "고속터미널"],
        "lines": ["6호선", "4호선", "9호선"],
        "clues": [
            {"type": "total_stations", "text": "총 정차역 수는 정확히 9개 역이다.", "val": 9},
            {"type": "avoid_station", "text": "7호선 환승역인 '총신대입구(이수)역'은 지나지 않았다.", "val": "총신대입구"},
            {"type": "river_crossings", "text": "한강을 정확히 1번 건넜다 (동작대교 구간).", "val": 1},
            {"type": "transfer_count", "text": "환승은 정확히 2회 발생했다.", "val": 2}
        ]
    },
    # MEDIUM 2
    {
        "id": "medium-2",
        "difficulty": "중간",
        "level": 2,
        "title": "도심 횡단과 여의도행",
        "story": "종각역에서 출발하여 여의도로 출근한 회사원의 경로. 도심을 빠져나가는 1호선 루트입니다.",
        "start": "종각",
        "end": "여의도",
        "solution": ["종각", "시청", "서울역", "남영", "용산", "노량진", "샛강", "여의도"],
        "lines": ["1호선", "9호선"],
        "clues": [
            {"type": "total_stations", "text": "총 정차역 수는 정확히 8개 역이다.", "val": 8},
            {"type": "transfer_count", "text": "환승은 정확히 1회 발생했다 (노량진역 환승).", "val": 1},
            {"type": "via_station", "text": "1호선 중심역인 '용산역'을 경유했다.", "val": "용산"}
        ]
    },
    # HARD 1
    {
        "id": "hard-1",
        "difficulty": "어려움",
        "level": 1,
        "title": "남북 관통: 시청에서 고속터미널까지",
        "story": "시청역에서 출발하여 고속터미널에 도착한 승객. 수많은 환승 경로 중 단 하나의 경로만 존재합니다.",
        "start": "시청",
        "end": "고속터미널",
        "solution": ["시청", "서울역", "숙대입구", "삼각지", "신용산", "이촌", "동작", "총신대입구", "내방", "고속터미널"],
        "lines": ["1호선", "4호선", "7호선"],
        "clues": [
            {"type": "total_stations", "text": "총 정차역 수는 정확히 10개 역이다.", "val": 10},
            {"type": "via_station", "text": "4호선/7호선 환승역인 '총신대입구역'을 경유했다.", "val": "총신대입구"},
            {"type": "avoid_station", "text": "1호선/9호선 환승역인 '노량진역'은 거치지 않았다.", "val": "노량진"},
            {"type": "transfer_count", "text": "환승은 정확히 2회 발생했다.", "val": 2}
        ]
    },
    # HARD 2
    {
        "id": "hard-2",
        "difficulty": "어려움",
        "level": 2,
        "title": "영등포에서 충무로까지의 야행",
        "story": "영등포에서 한밤중에 충무로 영화의 거리로 향한 승객의 우회 환승 경로입니다.",
        "start": "영등포",
        "end": "충무로",
        "solution": ["영등포", "신길", "대방", "노량진", "용산", "남영", "서울역", "회현", "명동", "충무로"],
        "lines": ["1호선", "4호선"],
        "clues": [
            {"type": "total_stations", "text": "총 정차역 수는 출발/도착 포함 정확히 10개 역이다.", "val": 10},
            {"type": "avoid_station", "text": "서울의 중심 환승역인 '시청역'은 거치지 않았다.", "val": "시청"},
            {"type": "avoid_station", "text": "금융 중심지 '여의도역'은 거치지 않았다.", "val": "여의도"},
            {"type": "transfer_count", "text": "환승은 단 1회(서울역)만 발생했다.", "val": 1}
        ]
    }
]

# Physical verification of every curated stage
print("=== VERIFYING CURATED STAGES ===")
for st in curated_stages:
    start, end = st["start"], st["end"]
    sol = st["solution"]
    all_p = find_all_simple_paths(start, end, max_len=14)
    
    # Check matching
    from find_perfect_puzzles import evaluate, is_minimal
    clue_tuples = []
    for c in st["clues"]:
        clue_tuples.append((c["type"], c["val"]))
        
    matches = [p for p in all_p if all(evaluate(p, ct, adj) for ct in clue_tuples)]
    assert len(matches) == 1, f"Failed uniqueness for {st['id']}: found {len(matches)} solutions!"
    assert matches[0] == sol, f"Mismatch in solution for {st['id']}!"
    
    # Check minimality
    minimal = is_minimal(all_p, clue_tuples, adj)
    print(f"[{st['difficulty']} - {st['title']}]")
    print(f"  Start: {start} -> End: {end} (Length: {len(sol)})")
    print(f"  Verified Unique Solution: {' -> '.join(sol)}")
    print(f"  Total Competing Paths: {len(all_p)}")
    print(f"  Minimal Clue Certified: {minimal}")
    print()

data_payload = {
    "line_colors": LINE_COLORS,
    "stations": STATIONS,
    "lines": LINES,
    "stages": curated_stages
}

with open("scripts/game_data.json", "w", encoding="utf-8") as f:
    json.dump(data_payload, f, ensure_ascii=False, indent=2)

print("game_data.json created successfully!")
