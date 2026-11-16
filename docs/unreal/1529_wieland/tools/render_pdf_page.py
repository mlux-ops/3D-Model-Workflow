"""Draw one page of a PDF, or one box of it, as a PNG picture.

Usage:
    python render_pdf_page.py <file.pdf> <page> <dots per inch> <out.png> [--box x0,y0,x1,y1]

The page is counted from 1. --box limits the picture to one rectangle of the
page, given in inches from the page's upper-left corner, so that small text
on a large drawing sheet can be read at a high resolution without drawing
the whole sheet.

Needs the pymupdf package. On this workstation it is not installed into
Python itself; it sits in E:\\Wieland1529_site_data\\_python_packages, and the
caller puts that folder on PYTHONPATH for this script only.
"""

import sys

import pymupdf


def main(argv):
    if len(argv) < 5:
        print(__doc__)
        return 2
    document = pymupdf.open(argv[1])
    page = document[int(argv[2]) - 1]
    dpi = float(argv[3])
    clip = None
    if "--box" in argv:
        x0, y0, x1, y1 = (float(v) * 72.0 for v in argv[argv.index("--box") + 1].split(","))
        clip = pymupdf.Rect(x0, y0, x1, y1)
    picture = page.get_pixmap(dpi=int(dpi), clip=clip, alpha=False)
    picture.save(argv[4])
    print("page %s of %d, %.1f x %.1f in, rotation %d -> %s, %d x %d pixels" % (
        argv[2], len(document), page.rect.width / 72.0, page.rect.height / 72.0, page.rotation, argv[4], picture.width, picture.height))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
