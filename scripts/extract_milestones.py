#!/usr/bin/env python3
"""
Extract milestone-tagged sections from split spec files and write to milestone markdown files.

Usage:
    python scripts/extract_milestones.py

Requirements:
    - Python 3.7+

Outputs:
    docs/milestones/milestone_XX_extracted.md for each milestone found
"""
import os
import re
from collections import defaultdict

INPUT_FILES = [
    "unmerged_spec_1.md",
    "unmerged_spec_2.md",
    "unmerged_spec_3.md",
]
OUTPUT_DIR = "docs/milestones"
MILESTONE_TAG_RE = re.compile(r"<!-- MILESTONE: ([A-Za-z0-9_]+) -->")
MILESTONE_END_RE = re.compile(r"<!-- /MILESTONE: ([A-Za-z0-9_]+) -->")


def extract_milestones_from_file(filepath):
    """
    Extracts all milestone-tagged sections from a file.
    Returns a dict: {milestone: [list of markdown lines]}
    Handles nested and overlapping tags.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    stack = []  # Stack of (milestone, start_line)
    milestone_content = defaultdict(list)  # milestone -> list of lines
    active_milestones = set()

    for i, line in enumerate(lines):
        start_match = MILESTONE_TAG_RE.match(line.strip())
        end_match = MILESTONE_END_RE.match(line.strip())
        if start_match:
            milestone = start_match.group(1)
            stack.append((milestone, i))
            active_milestones.add(milestone)
            continue
        if end_match:
            milestone = end_match.group(1)
            # Pop the last matching milestone from the stack
            for j in range(len(stack)-1, -1, -1):
                if stack[j][0] == milestone:
                    stack.pop(j)
                    break
            active_milestones.discard(milestone)
            continue
        # For all currently open milestones, add this line
        for milestone in active_milestones:
            milestone_content[milestone].append(line)
    return milestone_content


def main():
    all_milestone_content = defaultdict(list)
    for filepath in INPUT_FILES:
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found, skipping.")
            continue
        file_milestones = extract_milestones_from_file(filepath)
        for milestone, content in file_milestones.items():
            all_milestone_content[milestone].extend(content)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for milestone, content in all_milestone_content.items():
        outname = f"milestone_{milestone.lower()}.md"
        outpath = os.path.join(OUTPUT_DIR, outname)
        with open(outpath, "w", encoding="utf-8") as f:
            f.writelines(content)
        print(f"Extracted milestone {milestone}: {len(content)} lines -> {outpath}")

    print("Extraction complete. Milestones found:", ", ".join(sorted(all_milestone_content.keys())))

if __name__ == "__main__":
    main() 