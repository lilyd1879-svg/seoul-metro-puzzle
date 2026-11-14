"""
Categorize and curate certified puzzles by difficulty
"""
import json

with open("scripts/certified_puzzles.json", "r", encoding="utf-8") as f:
    puzzles = json.load(f)

print(f"Total puzzles: {len(puzzles)}")

by_diff = {"쉬움": [], "중간": [], "어려움": []}

for p in puzzles:
    length = p["path_length"]
    transfers = p["transfers"]
    k_clues = len(p["clues"])
    
    # Difficulty heuristic
    if length <= 6 and transfers <= 1:
        by_diff["쉬움"].append(p)
    elif length <= 9 and transfers <= 2:
        by_diff["중간"].append(p)
    else:
        by_diff["어려움"].append(p)

print(f"쉬움: {len(by_diff['쉬움'])}")
print(f"중간: {len(by_diff['중간'])}")
print(f"어려움: {len(by_diff['어려움'])}")

def print_samples(diff, count=3):
    print(f"\n=== {diff} SAMPLES ===")
    for p in by_diff[diff][:count]:
        print(f"Start: {p['start']} -> End: {p['end']}")
        print(f"Path ({p['path_length']} stations, {p['transfers']} transfers): {' -> '.join(p['path'])}")
        print(f"Lines: {p['line_sequence']}")
        print(f"Clues: {p['clues']}")
        print()

print_samples("쉬움")
print_samples("중간")
print_samples("어려움")
