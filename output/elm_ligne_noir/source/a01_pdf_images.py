"""Extract embedded JPEG (DCTDecode) and Flate RGB images from the two spec PDFs into
references/pdf_images/, with <=800 px thumbnails. Pure-python: no PDF library is installed."""
import io
import os
import re
import zlib

from PIL import Image

from guard import ref, out_path

PDFS = ["nemo_vivant_brochure.pdf", "elm_vivid_spec.pdf"]


def main():
    for pdf in PDFS:
        data = open(ref(pdf), "rb").read()
        stem = os.path.splitext(pdf)[0]
        n = 0
        for m in re.finditer(rb"<<(.{0,600}?)>>\s*stream\r?\n", data, re.S):
            d = m.group(1)
            if b"/Image" not in d:
                continue
            end = data.find(b"endstream", m.end())
            raw = data[m.end():end]
            w = re.search(rb"/Width\s+(\d+)", d)
            h = re.search(rb"/Height\s+(\d+)", d)
            if not (w and h):
                continue
            w, h = int(w.group(1)), int(h.group(1))
            if w < 300 or h < 300:
                continue
            try:
                if b"/DCTDecode" in d:
                    im = Image.open(io.BytesIO(raw))
                    im.load()
                elif b"/FlateDecode" in d and b"/DeviceRGB" in d:
                    px = zlib.decompress(raw)
                    im = Image.frombytes("RGB", (w, h), px[: w * h * 3])
                else:
                    continue
            except Exception as e:  # report and continue; one bad stream must not hide the rest
                print("skip", pdf, n, w, h, type(e).__name__, e)
                continue
            im = im.convert("RGB")
            name = "%s_%02d_%dx%d" % (stem, n, w, h)
            im.save(out_path("references/pdf_images/%s.png" % name))
            t = im.copy()
            t.thumbnail((800, 800), Image.LANCZOS)
            t.save(out_path("references/pdf_images/_thumbs/%s.jpg" % name), quality=88)
            print(name)
            n += 1


if __name__ == "__main__":
    main()
