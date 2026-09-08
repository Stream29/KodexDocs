"""Collapse preparation time without removing or manufacturing terminal output."""
import argparse
import json
from pathlib import Path


def collapse_preparation(events, seconds):
    if events[0]["version"] != 3 or seconds < 0:
        raise ValueError("Expected asciicast v3 and a nonnegative preparation duration")
    cutoff = round(seconds * 1_000_000)
    elapsed = previous = 0
    edited = [events[0]]
    for event in events[1:]:
        elapsed += round(event[0] * 1_000_000)
        current = max(0, elapsed - cutoff)
        edited.append([(current - previous) / 1_000_000, *event[1:]])
        previous = current
    return edited


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--before", type=float, required=True)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error("Keep the original recording; source and output must differ")
    events = [json.loads(line) for line in args.source.read_text().splitlines()]
    edited = collapse_preparation(events, args.before)
    args.output.write_text("".join(json.dumps(event, ensure_ascii=False) + "\n" for event in edited))
