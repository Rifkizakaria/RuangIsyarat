#!/usr/bin/env python
"""Extract MediaPipe hand landmarks from ASL dataset images and save to CSV.

Images are processed in parallel (one worker per letter) to speed up the
~7,800 image extraction. Each worker writes a temporary part file, which is
merged into a single CSV at the end.
"""
import csv
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import cv2
import mediapipe as mp

# Avoid UnicodeEncodeError on Windows consoles that use cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Paths (portable: relative to the project root)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "data" / "asl_dataset_raw"
CSV_FILE = PROJECT_ROOT / "dataset" / "asl_landmarks.csv"
PART_DIR = CSV_FILE.parent / "_landmark_parts"

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
IMAGE_EXTS = (".jpg", ".jpeg", ".png")

HEADER = ["label"]
for _i in range(21):
    HEADER.extend([f"x_{_i}", f"y_{_i}", f"z_{_i}"])


def normalize_landmarks(landmarks):
    """Normalize landmarks relative to the palm base (landmark 0)."""
    if landmarks is None or len(landmarks) != 63:
        return None

    base_x, base_y, base_z = landmarks[0], landmarks[1], landmarks[2]

    normalized = []
    for i in range(0, 63, 3):
        normalized.extend([
            round(landmarks[i] - base_x, 6),
            round(landmarks[i + 1] - base_y, 6),
            round(landmarks[i + 2] - base_z, 6),
        ])
    return normalized


def _extract_letter(job):
    """Worker: extract all images for one letter and write a part CSV."""
    letter, image_paths, part_file = job

    mp_hands = mp.solutions.hands
    rows = []
    found = 0
    no_hand = 0

    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.5,
    ) as hands:
        for image_path in image_paths:
            image = cv2.imread(image_path)
            if image is None:
                no_hand += 1
                continue

            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_image)

            if not results.multi_hand_landmarks:
                no_hand += 1
                continue

            landmarks = []
            for lm in results.multi_hand_landmarks[0].landmark:
                landmarks.extend([lm.x, lm.y, lm.z])

            normalized = normalize_landmarks(landmarks)
            if normalized is None:
                no_hand += 1
                continue

            rows.append([letter] + normalized)
            found += 1

    with open(part_file, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    return letter, len(image_paths), found, no_hand


def collect_images():
    """Return {letter: [image paths]} for available letter folders."""
    per_letter = {}
    for letter in LETTERS:
        letter_dir = DATASET_DIR / letter
        if not letter_dir.is_dir():
            continue
        paths = []
        for ext in IMAGE_EXTS:
            paths.extend(sorted(str(p) for p in letter_dir.glob(f"*{ext}")))
        per_letter[letter] = paths
        print(f"  Folder {letter}/: {len(paths)} gambar ditemukan", flush=True)
    return per_letter


def main():
    print("=" * 60)
    print("RuangIsyarat - ASL Landmark Extractor (parallel)")
    print("=" * 60)
    print(f"Dataset directory: {DATASET_DIR}")
    print(f"Output CSV: {CSV_FILE}")
    print()

    if not DATASET_DIR.exists():
        print(f"ERROR: Dataset directory not found: {DATASET_DIR}")
        sys.exit(1)

    per_letter = collect_images()
    total = sum(len(v) for v in per_letter.values())
    print(f"\nTotal images found: {total}")

    if total == 0:
        print("ERROR: Tidak ada gambar untuk diproses!")
        print("Pastikan struktur folder adalah:")
        print("  data/asl_dataset_raw/A/*.jpg")
        print("  data/asl_dataset_raw/B/*.jpg")
        print("  ... dst")
        sys.exit(1)

    PART_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [
        (letter, paths, str(PART_DIR / f"{letter}.csv"))
        for letter, paths in per_letter.items()
        if paths
    ]

    workers = max(1, min(4, (os.cpu_count() or 2)))
    print(f"Memproses dengan {workers} worker paralel...\n", flush=True)

    results = {}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_extract_letter, job): job[0] for job in jobs}
        for future in as_completed(futures):
            letter = futures[future]
            try:
                _, processed, found, no_hand = future.result()
                results[letter] = (processed, found, no_hand)
                print(
                    f"  Selesai {letter}: {found}/{processed} terdeteksi "
                    f"({no_hand} tanpa tangan)",
                    flush=True,
                )
            except Exception as exc:
                print(f"  GAGAL {letter}: {exc}", flush=True)

    # Merge parts in alphabetical order into the final CSV
    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    merged = 0
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(HEADER)
        for letter in LETTERS:
            part_file = PART_DIR / f"{letter}.csv"
            if not part_file.exists():
                continue
            with open(part_file, newline="", encoding="utf-8") as part:
                rows = list(csv.reader(part))
            writer.writerows(rows)
            merged += len(rows)

    # Cleanup temporary parts
    for part_file in PART_DIR.glob("*.csv"):
        part_file.unlink()
    try:
        PART_DIR.rmdir()
    except OSError:
        pass

    processed = sum(v[0] for v in results.values())
    found = sum(v[1] for v in results.values())
    no_hand = sum(v[2] for v in results.values())

    print()
    print("=== Results ===")
    print(f"Total images: {processed}")
    print(f"Hand detected: {found}")
    print(f"No hand detected: {no_hand}")
    print(f"Rows written to CSV: {merged}")
    print()
    print(f"CSV saved to: {CSV_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
