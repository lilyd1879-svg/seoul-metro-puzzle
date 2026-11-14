"""
Curate diverse, iconic stages with different start-end pairs across Easy, Medium, Hard.
"""
import json

with open("scripts/final_game_data.json", "r", encoding="utf-8") as f:
    full_data = json.load(f)

with open("scripts/certified_puzzles.json", "r", encoding="utf-8") as f:
    raw_puzzles = json.load(f)

from metro_data import STATIONS, LINES, LINE_COLORS
from verify_puzzles import build_graph, find_all_simple_paths
from find_perfect_puzzles import evaluate, is_minimal

adj = build_graph()

def clue_to_text(c_type, val):
    if c_type == "total_stations":
        return f"총 정차역 수는 출발/도착역을 포함하여 정확히 {val}개 역이다."
    elif c_type == "transfer_count":
        return f"환승은 정확히 {val}회 발생했다."
    elif c_type == "river_crossings":
        return f"한강을 정확히 {val}번 건넜다."
    elif c_type == "via_station":
        return f"주요 환승 거점인 '{val}역'을 경유했다."
    elif c_type == "avoid_station":
        return f"혼잡을 피해 '{val}역'은 거치지 않았다."
    elif c_type == "line_sequence":
        return f"탑승한 호선 순서는 [{' ➔ '.join(val)}]이다."
    return f"{c_type}: {val}"

# Pick best distinct stages
chosen = []

# 1. Easy Stage 1: 홍대입구 -> 여의도 (5 stations, 당산 경유, 영등포구청 회피)
for p in raw_puzzles:
    if p["start"] == "홍대입구" and p["end"] == "여의도" and p["path_length"] == 5:
        clues = [(c[0], c[1]) for c in p["clues"]]
        all_p = find_all_simple_paths("홍대입구", "여의도", 12)
        if is_minimal(all_p, clues, adj):
            chosen.append({
                "id": "easy-1",
                "difficulty": "쉬움",
                "level": 1,
                "title": "홍대에서 여의도: 황금 지름길",
                "story": "퇴근 시간 홍대입구에서 여의도 금융가로 향하는 승객의 9호선 환승 지름길을 밝히세요.",
                "start": "홍대입구",
                "end": "여의도",
                "path": p["path"],
                "path_length": p["path_length"],
                "transfers": p["transfers"],
                "lines": p["line_sequence"],
                "clues": [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in clues]
            })
            break

# 2. Easy Stage 2: 합정 -> 노량진 (6 stations, 2호선 -> 9호선)
for p in raw_puzzles:
    if p["start"] == "합정" and p["end"] == "노량진" and p["path_length"] == 6 and p["transfers"] == 1:
        clues = [(c[0], c[1]) for c in p["clues"]]
        all_p = find_all_simple_paths("합정", "노량진", 12)
        if is_minimal(all_p, clues, adj):
            chosen.append({
                "id": "easy-2",
                "difficulty": "쉬움",
                "level": 2,
                "title": "노량진 수산시장 특급",
                "story": "합정에서 노량진까지 9호선 급행 라인을 이용해 한강을 건넌 승객의 단 2개 단서 경로입니다.",
                "start": "합정",
                "end": "노량진",
                "path": p["path"],
                "path_length": p["path_length"],
                "transfers": p["transfers"],
                "lines": p["line_sequence"],
                "clues": [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in clues]
            })
            break

# 3. Medium Stage 1: 공덕 -> 고속터미널 (9 stations, 삼각지 경유, 4호선/9호선)
for p in raw_puzzles:
    if p["start"] == "공덕" and p["end"] == "고속터미널" and p["path_length"] == 9:
        clues = [(c[0], c[1]) for c in p["clues"]]
        all_p = find_all_simple_paths("공덕", "고속터미널", 13)
        if is_minimal(all_p, clues, adj):
            chosen.append({
                "id": "medium-1",
                "difficulty": "중간",
                "level": 1,
                "title": "동작대교와 강남 터미널",
                "story": "마포 권역 공덕에서 출발하여 동작대교를 건너 고속터미널에 도착한 승객의 2회 환승 루트입니다.",
                "start": "공덕",
                "end": "고속터미널",
                "path": p["path"],
                "path_length": p["path_length"],
                "transfers": p["transfers"],
                "lines": p["line_sequence"],
                "clues": [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in clues]
            })
            break

# 4. Medium Stage 2: 종각 -> 여의도 (8 stations, 1호선 -> 9호선 노량진 환승)
for p in raw_puzzles:
    if p["start"] == "종각" and p["end"] == "여의도" and p["path_length"] == 8 and p["transfers"] == 1:
        clues = [(c[0], c[1]) for c in p["clues"]]
        all_p = find_all_simple_paths("종각", "여의도", 13)
        if is_minimal(all_p, clues, adj):
            chosen.append({
                "id": "medium-2",
                "difficulty": "중간",
                "level": 2,
                "title": "도심 탈출: 종각에서 여의도",
                "story": "종각역에서 출발하여 1호선 급행 축을 타고 여의도 업무지구로 출근한 직장인의 최적 경로입니다.",
                "start": "종각",
                "end": "여의도",
                "path": p["path"],
                "path_length": p["path_length"],
                "transfers": p["transfers"],
                "lines": p["line_sequence"],
                "clues": [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in clues]
            })
            break

# 5. Hard Stage 1: 시청 -> 고속터미널 (10 stations, 총신대입구 경유, 1->4->7호선)
for p in raw_puzzles:
    if p["start"] == "시청" and p["end"] == "고속터미널" and p["path_length"] == 10:
        clues = [(c[0], c[1]) for c in p["clues"]]
        all_p = find_all_simple_paths("시청", "고속터미널", 13)
        if is_minimal(all_p, clues, adj):
            chosen.append({
                "id": "hard-1",
                "difficulty": "어려움",
                "level": 1,
                "title": "서울 남북 관통: 7호선의 트릭",
                "story": "시청역에서 출발해 고속터미널로 향한 승객. 9호선 대신 7호선 총신대입구 환승을 택한 고난도 유일 경로.",
                "start": "시청",
                "end": "고속터미널",
                "path": p["path"],
                "path_length": p["path_length"],
                "transfers": p["transfers"],
                "lines": p["line_sequence"],
                "clues": [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in clues]
            })
            break

# 6. Hard Stage 2: 영등포 -> 충무로 (10 stations, 1호선 서울역 -> 4호선 명동 경유)
for p in raw_puzzles:
    if p["start"] == "영등포" and p["end"] == "충무로" and p["path_length"] == 10:
        clues = [(c[0], c[1]) for c in p["clues"]]
        all_p = find_all_simple_paths("영등포", "충무로", 13)
        if is_minimal(all_p, clues, adj):
            chosen.append({
                "id": "hard-2",
                "difficulty": "어려움",
                "level": 2,
                "title": "충무로 심야 영화제행",
                "story": "영등포에서 출발하여 중심가 시청역과 여의도역을 모두 피해서 충무로에 도착한 심야 승객의 경로.",
                "start": "영등포",
                "end": "충무로",
                "path": p["path"],
                "path_length": p["path_length"],
                "transfers": p["transfers"],
                "lines": p["line_sequence"],
                "clues": [{"type": c[0], "val": c[1], "text": clue_to_text(c[0], c[1])} for c in clues]
            })
            break

print(f"Total curated diverse stages: {len(chosen)}")
for c in chosen:
    print(f"[{c['difficulty']} - {c['title']}] {c['start']} -> {c['end']} ({c['path_length']}역, 환승 {c['transfers']}회)")
    print(f"   Route: {' -> '.join(c['path'])}")
    for clue in c["clues"]:
        print(f"   - {clue['text']}")
    print()

output_data = {
    "line_colors": LINE_COLORS,
    "stations": STATIONS,
    "lines": LINES,
    "stages": chosen
}

with open("scripts/final_curated_data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
