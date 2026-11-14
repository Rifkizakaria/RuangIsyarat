#!/usr/bin/env python
"""Train ASL model from landmark dataset and save as .pkl."""
import os
import sys
import csv
import numpy as np
from pathlib import Path

# Avoid UnicodeEncodeError on Windows consoles that use cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Paths (portable: relative to the project root)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = PROJECT_ROOT / "dataset" / "asl_landmarks.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_FILE = MODEL_DIR / "model_asl.pkl"

print("=" * 60)
print("RuangIsyarat - ASL Model Trainer")
print("=" * 60)
print(f"Input: {CSV_FILE}")
print(f"Output: {MODEL_FILE}")
print()

# Validasi file CSV
if not CSV_FILE.exists():
    print(f"❌ File CSV tidak ditemukan: {CSV_FILE}")
    print("Jalankan langkah ekstraksi landmark terlebih dahulu:")
    print("  python scripts/extract_landmarks.py")
    sys.exit(1)

# Baca CSV
print(" membaca CSV...")
with open(CSV_FILE, mode="r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  # skip header
    data_rows = list(reader)

print(f"Total baris data: {len(data_rows)}")

# Pisahkan fitur dan label
X = []
y = []
for row in data_rows:
    label = row[0]
    features = [float(x) for x in row[1:]]
    if len(features) != 63:
        print(f"⚠️ Peringatan: baris memiliki {len(features)} fitur, expected 63")
        continue
    X.append(features)
    y.append(label)

print(f"Data valid: {len(X)} sampel")

if len(X) < 10:
    print("❌ Terlalu sedikit data valid. Minimal 10 sampel yang memiliki 63 fitur.")
    sys.exit(1)

# Encode label ke angka
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_encoded = le.fit_transform(y)

print(f"Label unik: {list(le.classes_)}")

# Split data sederhana (80/20)
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Latih model RandomForest
from sklearn.ensemble import RandomForestClassifier
print("Melatih RandomForestClassifier...")
clf = RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    random_state=42,
    min_samples_split=2,
    min_samples_leaf=1
)
clf.fit(X_train, y_train)

# Evaluasi
train_acc = clf.score(X_train, y_train) * 100
test_acc = clf.score(X_test, y_test) * 100
print(f"Akurasi training: {train_acc:.2f}%")
print(f"Akurasi testing:  {test_acc:.2f}%")

if test_acc < 70:
    print("⚠️ Peringatan: Akurasi testing di bawah 70%. Tambah data atau perbaiki ekstraksi landmark.")

# Simpan model ke file .pkl
MODEL_DIR.mkdir(parents=True, exist_ok=True)

import pickle
model_data = {
    "model": clf,
    "label_encoder": le,
    "classes": list(le.classes_),
    "train_accuracy": train_acc,
    "test_accuracy": test_acc,
    "n_samples": len(X),
    "n_features": 63
}

with open(MODEL_FILE, "wb") as f:
    pickle.dump(model_data, f)

print()
print(f"✅ Model berhasil disimpan ke: {MODEL_FILE}")
print("=" * 60)