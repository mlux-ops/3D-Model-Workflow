"""Copy named sheets out of a drawing set (one PDF) and save the text on them.

Usage:
    python extract_drawing_sheets.py <drawing set .pdf> --list
    python extract_drawing_sheets.py <drawing set .pdf> <output folder> <page>=<name> [<page>=<name> ...]
    python extract_drawing_sheets.py <one-sheet .pdf> --images <output folder> <prefix>

--images writes every picture embedded in the PDF's pages (a scanned survey
placed on a sheet, for instance) as its own file, so it can be looked at.

--list prints, for every page, its size in inches and the sheet numbers found
in its text (such as T1.1 or A2.1), with a few words that follow each, so
that the page holding a given sheet can be told. Pages are counted from 1.

The second form writes each named page as its own one-page PDF,
<name>.pdf, and the text found on it as <name>.txt, into the output folder.
The drawing set itself is only read.

Needs the pypdf package.
"""

import os
import re
import sys

from pypdf import PdfReader, PdfWriter

SHEET_NUMBER = re.compile(r"\b([A-Z]{1,2}\d{1,2}\.\d{1,2})\b")


def list_pages(reader):
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            text = ""
            print("page %d: text could not be read (%r)" % (index, exc))
        counts = {}
        for match in SHEET_NUMBER.finditer(text):
            counts[match.group(1)] = counts.get(match.group(1), 0) + 1
        common = sorted(counts.items(), key=lambda item: -item[1])[:4]
        width = float(page.mediabox.width) / 72.0
        height = float(page.mediabox.height) / 72.0
        words = " ".join(text.split())
        title = ""
        for key in ("SURVEY", "SITE PLAN", "PLAT"):
            position = words.upper().find(key)
            if position >= 0:
                title += " [%s: ...%s...]" % (key, words[max(0, position - 30):position + 50])
        print("page %3d  %5.1f x %5.1f in  text %6d chars  sheet numbers %s%s" % (
            index, width, height, len(text), ", ".join("%s x%d" % item for item in common) or "-", title[:260]))


def save_images(reader, folder, prefix):
    """Write every picture embedded in the PDF's pages into folder, as <prefix>_p<page>_<n>.<ext>."""
    os.makedirs(folder, exist_ok=True)
    for index, page in enumerate(reader.pages, start=1):
        count = 0
        for image in page.images:
            count += 1
            extension = os.path.splitext(image.name)[1] or ".bin"
            out = os.path.join(folder, "%s_p%d_%d%s" % (prefix, index, count, extension))
            with open(out, "wb") as handle:
                handle.write(image.data)
            size = ""
            try:
                size = " %d x %d pixels" % image.image.size
            except Exception:
                pass
            print("page %d picture %d -> %s (%d bytes)%s" % (index, count, out, os.path.getsize(out), size))
        if not count:
            print("page %d holds no embedded picture" % index)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    reader = PdfReader(argv[1])
    print("pages: %d" % len(reader.pages))
    if argv[2] == "--list":
        list_pages(reader)
        return 0
    if argv[2] == "--images":
        save_images(reader, argv[3], argv[4])
        return 0
    folder = argv[2]
    os.makedirs(folder, exist_ok=True)
    for item in argv[3:]:
        number, name = item.split("=", 1)
        page = reader.pages[int(number) - 1]
        writer = PdfWriter()
        writer.add_page(page)
        out_pdf = os.path.join(folder, name + ".pdf")
        with open(out_pdf, "wb") as handle:
            writer.write(handle)
        text = page.extract_text() or ""
        with open(os.path.join(folder, name + ".txt"), "w", encoding="utf-8") as handle:
            handle.write(text)
        print("page %s -> %s (%d bytes), text %d chars" % (number, out_pdf, os.path.getsize(out_pdf), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
