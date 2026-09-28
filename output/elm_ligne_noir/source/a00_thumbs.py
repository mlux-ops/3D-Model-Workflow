"""Make <=800 px thumbnails of every reference image into references/_thumbs, and rename the
ELM CDN files to readable names (copies; the originals stay)."""
import glob
import os
import shutil

from PIL import Image

from guard import INPUT_DIR, out_path

NAMES = {
    "6508c8490fee3dfe75083b50": "elm_page_prefab_1",
    "6508c8490fee3dfe75083b56": "elm_page_prefab_2",
    "6508c8490fee3dfe75083b6d": "elm_page_prefab_3",
    "6508c8490fee3dfe75083b70": "elm_page_prefab_4",
    "6508c8490fee3dfe75083b74": "elm_page_prefab_5",
    "6508c8490fee3dfe75083b76": "elm_page_prefab_6",
    "6508c8490fee3dfe75083b86": "elm_page_prefab_7",
    "6508c8490fee3dfe75083b87": "elm_page_main-image_template",
    "6508c8490fee3dfe75083b88": "elm_page_prefab_8_portrait",
    "67b400be30ee5e8f7402ca58": "elm_ligne-noir_1",
    "67b400bea14ebddfa7100ad5": "elm_ligne-noir_2",
    "67b400c2739c890c37f35d5c": "elm_ligne-noir_3",
    "6a3c3388480f4c9041c96877": "elm_vivid_spec",
}


def main():
    for f in sorted(glob.glob(os.path.join(INPUT_DIR, "*"))):
        if os.path.isdir(f):
            continue
        base = os.path.basename(f)
        key = base.split("_")[0]
        if key not in NAMES:
            continue
        ext = os.path.splitext(base)[1].lower().replace(".jpeg", ".jpg")
        dst = out_path("references/" + NAMES[key] + ext)
        if not os.path.exists(dst):
            shutil.copyfile(f, dst)
        if ext == ".pdf":
            continue
        im = Image.open(dst).convert("RGB")
        im.thumbnail((800, 800), Image.LANCZOS)
        im.save(out_path("references/_thumbs/" + NAMES[key] + ".jpg"), quality=90)
        print(NAMES[key], Image.open(dst).size)


if __name__ == "__main__":
    main()
