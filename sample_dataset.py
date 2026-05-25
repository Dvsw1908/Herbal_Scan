import random
import shutil
from pathlib import Path

SEED = 42
random.seed(SEED)

SRC_TRAIN = Path("data/final")
SRC_TEST  = Path("data/test_final")
DST_OUT   = Path("data/sampled")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
TOTAL_PER_CLASS = 100
MIN_FROM_TRAIN  = 80
MAX_FROM_TRAIN  = 99


def get_images(folder: Path) -> list[Path]:
    return [f for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTS]


def copy_images_numbered(images: list[Path], dst_dir: Path, start: int = 1):
    """Salin dan rename file jadi testing_1.jpg, testing_2.jpg, dst."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(images, start=start):
        ext = img.suffix.lower()
        shutil.copy2(img, dst_dir / f"testing_{i}{ext}")


if __name__ == "__main__":
    if DST_OUT.exists():
        shutil.rmtree(DST_OUT)

    # Ambil kelas dari kedua folder, cocokkan pakai lowercase
    train_map = {d.name.lower(): d for d in SRC_TRAIN.iterdir() if d.is_dir()}
    test_map  = {d.name.lower(): d for d in SRC_TEST.iterdir()  if d.is_dir()}
    common_keys = sorted(train_map.keys() & test_map.keys())

    print(f"{'='*55}")
    print(f"Kelas ditemukan di kedua folder: {len(common_keys)}")
    print(f"Target per kelas : {TOTAL_PER_CLASS} foto")
    print(f"Dari data/final  : {MIN_FROM_TRAIN}–{MAX_FROM_TRAIN} foto (acak)")
    print(f"Sisanya          : dari data/test_final")
    print(f"{'='*55}")

    grand_total = 0
    for key in common_keys:
        train_dir = train_map[key]
        test_dir  = test_map[key]
        cls = test_dir.name  # pakai nama dari test_final sebagai nama output

        train_imgs = get_images(train_dir)
        test_imgs  = get_images(test_dir)

        n_from_train = random.randint(MIN_FROM_TRAIN, MAX_FROM_TRAIN)
        n_from_train = min(n_from_train, len(train_imgs))
        n_from_test  = TOTAL_PER_CLASS - n_from_train
        n_from_test  = min(n_from_test, len(test_imgs))

        sampled_train = random.sample(train_imgs, n_from_train)
        sampled_test  = random.sample(test_imgs,  n_from_test)

        dst_dir = DST_OUT / cls
        all_sampled = sampled_train + sampled_test
        random.shuffle(all_sampled)
        copy_images_numbered(all_sampled, dst_dir, start=1)

        total_cls = n_from_train + n_from_test
        grand_total += total_cls
        print(f"  {cls:<35} → {total_cls} foto  (final: {n_from_train}, test_final: {n_from_test})")

    print(f"\n  Grand total: {grand_total} foto")
    print(f"\nSelesai! Data tersimpan di {DST_OUT}")
