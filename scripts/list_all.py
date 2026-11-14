"""
List puzzles by unique start-end pairs and show clues
"""
import json

with open("scripts/certified_puzzles.json", "r", encoding="utf-8") as f:
    puzzles = json.load(f)

seen_pairs = set()
for p in puzzles:
    pair = (p["start"], p["end"])
    print(f"[{p['start']} -> {p['end']}] (Len: {p['path_length']}, Transfers: {p['transfers']}, Clues: {len(p['clues'])})")
    print(f"   Route: {' -> '.join(p['path'])}")
    print(f"   Lines: {p['line_sequence']}")
    print(f"   Clues: {p['clues']}")
    print("-" * 60)
