"""
Detailed inspection of paths and clues.
"""
from metro_data import STATIONS, LINES, HAN_RIVER_CROSSINGS
from verify_puzzles import build_graph, find_all_simple_paths, get_line_sequence, count_river_crossings

adj = build_graph()

def inspect_pair(start, end, max_len=13):
    paths = find_all_simple_paths(start, end, max_len)
    print(f"\n=== {start} -> {end} (Total {len(paths)} paths up to len {max_len}) ===")
    for i, p in enumerate(paths):
        lines = get_line_sequence(p, adj)
        rc = count_river_crossings(p)
        print(f"Path {i+1} (len {len(p)}): {' -> '.join(p)}")
        print(f"   Lines: {lines}, Han Crossings: {rc}")

inspect_pair("합정", "노량진", 11)
inspect_pair("을지로3가", "여의도", 11)
inspect_pair("시청", "고속터미널", 12)
inspect_pair("홍대입구", "여의도", 10)
