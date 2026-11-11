from pathlib import Path
R=Path(__file__).resolve().parents[1]
changed=0
for f in sorted((R/'rooms').glob('PH-*/board/round-004/critic-cost.md')):
    original=f.read_text(encoding='utf-8')
    old='../../../../../research/'
    new='../../../../research/'
    n=original.count(old)
    if n:
        revised=original.replace(old,new)
        f.write_text(revised,encoding='utf-8')
        changed+=n
        print(f.parent.parent.parent.name,n)
assert changed==28,changed
print('PASS 28 relative citation links corrected; rubric text/scores unchanged')
