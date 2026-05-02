"""
test_note_cutout.py
-------------------
Tests ONLY the note-boundary detection and cutout portions of the pipeline.
CREPE pitch detection is intentionally skipped — this script validates that:
  1. find_notes() correctly identifies note start/end boundaries
  2. cutout_notes() correctly slices the audio into individual segments
  3. Each cutout segment has a sensible duration and amplitude

Run from the Josh_coded directory:
    python3 test_note_cutout.py
"""

import sys
import os
import numpy as np
from scipy.io import wavfile

# Patch out crepe before importing helpers so we don't need it installed
import unittest.mock as mock
sys.modules['crepe'] = mock.MagicMock()

import note_cutout_helpers as helpers

# ── Config ────────────────────────────────────────────────────────────────────
WAV_FILE = "input_files/Track 1_002.wav"
MIN_NOTE_DURATION_S = 0.15   # seconds — notes shorter than this are suspicious
MAX_NOTE_DURATION_S = 15.0   # seconds — notes longer than this are suspicious


def run_tests():
    print("=" * 60)
    print("NOTE CUTOUT TEST")
    print("=" * 60)

    # ── 1. Load the file ──────────────────────────────────────────────────────
    if not os.path.exists(WAV_FILE):
        print(f"ERROR: Test file not found: {WAV_FILE}")
        sys.exit(1)

    sr, data = wavfile.read(WAV_FILE)
    duration = len(data) / sr
    print(f"\n[Input file]")
    print(f"  File     : {WAV_FILE}")
    print(f"  Sample rate: {sr} Hz")
    print(f"  Channels : {'stereo' if len(data.shape) == 2 else 'mono'}")
    print(f"  Duration : {duration:.2f}s  ({len(data):,} samples)")

    # ── 2. Detect note boundaries ─────────────────────────────────────────────
    print("\n[Step 1: find_notes()]")
    boundaries = helpers.find_notes(data, sr)

    if not boundaries:
        print("  FAIL — No note boundaries detected at all.")
        sys.exit(1)

    print(f"  Found {len(boundaries)} note boundary/boundaries.")

    # ── 3. Print each boundary ────────────────────────────────────────────────
    print("\n  # │  Start (s)  │   End (s)  │  Duration (s)  │  Status")
    print("  ─" * 14)
    all_passed = True
    for i, (start, end) in enumerate(boundaries):
        start_s = start / sr
        end_s   = end / sr
        dur_s   = end_s - start_s

        if dur_s < MIN_NOTE_DURATION_S:
            status = f"WARN — too short (<{MIN_NOTE_DURATION_S}s)"
            all_passed = False
        elif dur_s > MAX_NOTE_DURATION_S:
            status = f"WARN — very long (>{MAX_NOTE_DURATION_S}s)"
        else:
            status = "OK"

        print(f"  {i:>2} │  {start_s:>8.3f}   │  {end_s:>8.3f}  │    {dur_s:>8.3f}    │  {status}")

    # ── 4. Cut out the notes ──────────────────────────────────────────────────
    print("\n[Step 2: cutout_notes()]")
    notes_dict = helpers.cutout_notes(data, boundaries)

    if len(notes_dict) != len(boundaries):
        print(f"  FAIL — cutout_notes() returned {len(notes_dict)} segments but expected {len(boundaries)}.")
        all_passed = False
    else:
        print(f"  cutout_notes() returned {len(notes_dict)} segment(s). ✓")

    # ── 5. Validate each cutout segment ──────────────────────────────────────
    print("\n[Step 3: Segment validation]")
    for i, seg in notes_dict.items():
        seg_dur = len(seg) / sr
        # Check amplitude — a valid note should have some energy
        if len(seg.shape) == 2:
            seg_mono = seg.astype(np.float32).mean(axis=1)
        else:
            seg_mono = seg.astype(np.float32)

        peak = np.max(np.abs(seg_mono))
        rms  = np.sqrt(np.mean(seg_mono ** 2))

        status = "OK" if peak > 0 and seg_dur >= MIN_NOTE_DURATION_S else "WARN — silent or too short"
        print(f"  Segment {i:>2}: dur={seg_dur:.3f}s  peak={peak:.1f}  rms={rms:.1f}  → {status}")

    # ── 6. Summary ────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    if all_passed:
        print("RESULT: All checks passed. Note cutout appears to be working correctly.")
    else:
        print("RESULT: Some checks raised warnings — review output above.")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
