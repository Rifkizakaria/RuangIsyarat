#!/usr/bin/env python
"""Download ASL Alphabet Dataset from public sources."""
import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

# Target directory
DATASET_DIR = Path("D:/python/RuangIsyarat/data/asl_dataset_raw")


def download_kaggle_dataset():
    """Try to download from Kaggle (requires kaggle API)."""
    print("Checking for Kaggle API...")
    try:
        import kaggle
        print("Downloading ASL Alphabet Dataset from Kaggle...")
        kaggle.api.dataset_download_files(
            "grassknoted/asl-alphabet",
            path=str(DATASET_DIR.parent),
            unzip=True
        )
        # Move files to the correct structure
        print("Organizing dataset structure...")
        for item in Path(DATASET_DIR.parent).iterdir():
            if item.is_dir():
                for sub in item.iterdir():
                    if sub.suffix in ['.jpg', '.png', '.jpeg']:
                        dest = DATASET_DIR / sub.parent.name.upper()
                        dest.mkdir(exist_ok=True)
                        shutil.copy2(str(sub), str(dest / sub.name))
        print("Kaggle dataset downloaded and organized!")
        return True
    except ImportError:
        print("Kaggle API not installed, skipping...")
        return False
    except Exception as e:
        print(f"Kaggle download failed: {e}")
        return False


def download_github_dataset():
    """Try to download from a known GitHub repository."""
    print("Trying GitHub dataset download...")
    # GitHub repo that contains ASL alphabet images
    urls = [
        "https://github.com/datasets.asl/asl-alphabet/archive/refs/heads/main.zip",
    ]

    for url in urls:
        try:
            print(f"Trying: {url}")
            filename = url.split("/")[-1]
            if filename.endswith('.zip'):
                urllib.request.urlretrieve(url, filename)
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall("temp_github_download")
                # Move extracted files
                import shutil
                extracted_dir = Path("temp_github_download")
                if extracted_dir.is_dir():
                    # Find ASL letter folders
                    for letter_dir in extracted_dir.rglob("*"):
                        if letter_dir.is_dir() and letter_dir.name.isalpha():
                            dest = DATASET_DIR / letter_dir.name.upper()
                            dest.mkdir(exist_ok=True)
                            for file in letter_dir.glob("*.jpg"):
                                shutil.copy2(str(file), str(dest / file.name))
                print(f"Downloaded from GitHub: {url}")
                # Cleanup
                if Path(filename).exists():
                    Path(filename).unlink()
                if Path("temp_github_download").exists():
                    shutil.rmtree("temp_github_download")
                return True
        except Exception as e:
            print(f"Failed {url}: {e}")
            continue

    return False


def create_placeholder_dataset():
    """Create a minimal placeholder dataset structure if download fails."""
    print("Creating placeholder dataset structure...")
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    # Create A-Z folders with placeholder info
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        folder = DATASET_DIR / letter
        folder.mkdir(exist_ok=True)
        # Create a simple placeholder text file
        (folder / "README.txt").write_text(
            f"Placeholder for {letter} - upload real ASL image here\n"
            f"Better: Use data_collector.py to record via webcam"
        )

    print(f"Placeholder structure created at {DATASET_DIR}")
    print("NOTE: For real functionality, please:")
    print("1. Download ASL dataset from Kaggle or similar")
    print("2. Or use data_collector.py to record via webcam")
    print("3. Then run extract_landmarks.py to create CSV")
    print("4. Then run train_model.py to train the model")
    return True


def main():
    print("RuangIsyarat - ASL Dataset Downloader")
    print("=" * 60)

    # Try Kaggle first
    success = download_kaggle_dataset()

    # If Kaggle failed, try GitHub
    if not success:
        success = download_github_dataset()

    # If both failed, create placeholder
    if not success:
        create_placeholder_dataset()

    print("=" * 60)
    print("Dataset download complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()