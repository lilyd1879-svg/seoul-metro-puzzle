"""
Extract exactly certified minimal puzzles where is_minimal == True.
"""
import json
from metro_data import STATIONS, LINES, LINE_COLORS, HAN_RIVER_CROSSINGS
from verify_puzzles import build_graph, find_all_simple_paths, get_line_sequence, count_river_crossings
from find_perfect_puzzles import evaluate, is_minimal

adj = build_graph()

with open("scripts/certified_puzzles.json", "r", encoding="utf-8") as f:
    raw_puzzles = json.load(f)

print(f"Total raw candidates: {len(raw_puzzles)}")

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

strictly_minimal_stages = []

# Group by start, end
for p in raw_puzzles:
    start, end = p["start"], p["end"]
    sol = p["path"]
    all_p = find_all_simple_paths(start, end, max_len=14)
    clues = [(c[0], c[1]) for c in p["clues"]]
    
    # Verify uniqueness
    matches = [path for path in all_p if all(evaluate(path, c, adj) for c in clues)]
    if len(matches) != 1 or matches[0] != sol:
        continue
        
    # Verify strict minimality
    if not is_minimal(all_p, clues, adj):
        continue
        
    # Format clues
    clue_objs = []
    for c_type, val in clues:
        clue_objs.append({
            "type": c_type,
            "val": val,
            "text": clue_to_text(c_type, val)
        })
        
    stage_obj = {
        "start": start,
        "end": end,
        "path": sol,
        "path_length": p["path_length"],
        "transfers": p["transfers"],
        "lines": p["line_sequence"],
        "clues": clue_objs,
        "clue_count": len(clues),
        "competing_paths": len(all_p)
    }
    strictly_minimal_stages.append(stage_obj)

print(f"Strictly minimal certified stages: {len(strictly_minimal_stages)}")

# Let's organize into Easy, Medium, Hard
stages_by_diff = {"쉬움": [], "중간": [], "어려움": []}

for st in strictly_minimal_stages:
    length = st["path_length"]
    transfers = st["transfers"]
    k_clues = st["clue_count"]
    
    # Deduplicate start-end
    pair = (st["start"], st["end"], tuple(st["path"]))
    
    if length <= 6 and transfers <= 1:
        stages_by_diff["쉬움"].append(st)
    elif length <= 9 and transfers <= 2:
        stages_by_diff["중간"].append(st)
    else:
        stages_by_diff["어려움"].append(st)

print("쉬움:", len(stages_by_diff["쉬움"]))
print("중간:", len(stages_by_diff["중간"]))
print("어려움:", len(stages_by_diff["어려움"]))

# Save top 3 for each difficulty
final_stages = []
stage_id = 1

titles_easy = [
    ("홍대에서 여의도: 9호선 지름길", "퇴근 시간 홍대입구에서 여의도 금융가로 향하는 승객의 최소 단서 경로를 밝히세요."),
    ("한강을 건너는 노량진 특급", "합정에서 노량진으로 직통 이동하는 승객의 환승 미스터리입니다."),
    ("당산 환승의 법칙", "2호선에서 5호선으로 갈아타는 출퇴근 승객의 정확한 이동 경로입니다.")
]

titles_medium = [
    ("동작대교를 건너는 사람들", "공덕에서 고속터미널까지 이동하는 승객의 9호선/4호선 복합 경로를 추리하세요."),
    ("종각에서 여의도까지의 도심 출근", "종각에서 시작해 도심을 벗어나 여의도에 도착한 승객의 경로입니다."),
    ("충무로 야간 극장행", "영등포에서 출발하여 명동을 거쳐 충무로로 이동한 승객의 1회 환승 경로입니다.")
]

titles_hard = [
    ("시청에서 고속터미널: 남북 종단", "수많은 우회로가 존재하는 서울의 남북 축. 총신대입구를 경유하는 10개 역 유일 경로."),
    ("도심 순환의 함정", "합정에서 노량진까지 도심을 크게 우회하여 이동한 의문의 장거리 경로."),
    ("여의도에서 강남: 황금 노선", "사당을 거쳐 여의도로 향하는 복잡한 환승망 속의 유일한 이동 경로.")
]

for idx, st in enumerate(stages_by_diff["쉬움"][:3]):
    st["id"] = f"easy-{idx+1}"
    st["difficulty"] = "쉬움"
    st["level"] = idx + 1
    st["title"] = titles_easy[idx][0]
    st["story"] = titles_easy[idx][1]
    final_stages.append(st)

for idx, st in enumerate(stages_by_diff["중간"][:3]):
    st["id"] = f"medium-{idx+1}"
    st["difficulty"] = "중간"
    st["level"] = idx + 1
    st["title"] = titles_medium[idx][0]
    st["story"] = titles_medium[idx][1]
    final_stages.append(st)

for idx, st in enumerate(stages_by_diff["어려움"][:3]):
    st["id"] = f"hard-{idx+1}"
    st["difficulty"] = "어려움"
    st["level"] = idx + 1
    st["title"] = titles_hard[idx][0]
    st["story"] = titles_hard[idx][1]
    final_stages.append(st)

game_data = {
    "line_colors": LINE_COLORS,
    "stations": STATIONS,
    "lines": LINES,
    "stages": final_stages
}

with open("scripts/final_game_data.json", "w", encoding="utf-8") as f:
    json.dump(game_data, f, ensure_ascii=False, indent=2)

print("\nFinal verified stages saved! Count:", len(final_stages))
