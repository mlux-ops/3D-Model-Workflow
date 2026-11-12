"""Journal helper for phase8_results.md, so that text with backslashes never passes through a shell.

    python journal.py done J3 outcome.txt     replace the PENDING cell of row J3 with the file's text
    python journal.py add J4 step.txt         append a row J4 (time from the clock) with the file's text, PENDING

The text files are single paragraphs; line breaks in them are joined with a space.
"""
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JOURNAL = os.path.normpath(os.path.join(HERE, "..", "..", "..", "phase8_results.md"))
MARK = "<!-- journal ends -->"


def text_of(path):
    with open(path, "r", encoding="utf-8") as handle:
        text = " ".join(line.strip() for line in handle.read().splitlines() if line.strip())
    bad = [c for c in text if ord(c) < 32]
    if bad or "|" in text:
        raise SystemExit("control character or table bar in " + path)
    return text


def main(argv):
    mode, number, path = argv[1], argv[2], argv[3]
    with open(JOURNAL, "r", encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    now = datetime.datetime.now().strftime("%H:%M")
    text = text_of(path)
    if mode == "done":
        for i, line in enumerate(lines):
            if line.startswith("| %s |" % number) and line.endswith("| PENDING |"):
                lines[i] = line[: -len("PENDING |")] + "DONE %s. %s |" % (now, text)
                break
        else:
            raise SystemExit("no PENDING row " + number)
    elif mode == "add":
        if any(line.startswith("| %s |" % number) for line in lines):
            raise SystemExit("row exists: " + number)
        last = max(i for i, line in enumerate(lines) if line.startswith("| J"))
        lines.insert(last + 1, "| %s | %s | %s | PENDING |" % (number, now, text))
    else:
        raise SystemExit(__doc__)
    with open(JOURNAL, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
    print(mode, number, now)


if __name__ == "__main__":
    main(sys.argv)
