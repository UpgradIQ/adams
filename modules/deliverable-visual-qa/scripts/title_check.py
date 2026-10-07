import re, subprocess, sys
xml = subprocess.run(['pdftotext', '-bbox-layout', sys.argv[1], '-'], capture_output=True, text=True).stdout
LINE = re.compile(r'<line xMin="([^"]+)" yMin="([^"]+)" xMax="([^"]+)" yMax="([^"]+)">(.*?)</line>', re.S)
fails = 0
for pno, page in enumerate(re.findall(r'<page .*?</page>', xml, re.S), 1):
    blocks = []
    for b in re.findall(r'<block .*?</block>', page, re.S):
        lines = LINE.findall(b)
        if not lines:
            continue
        blocks.append({
            'h': max(float(l[3]) - float(l[1]) for l in lines),
            'top': min(float(l[1]) for l in lines),
            'n': len(lines),
            'text': ' '.join(' '.join(re.sub(r'<[^>]+>', ' ', l[4]).split()) for l in lines),
        })
    if not blocks:
        continue
    title = max(blocks, key=lambda b: b['h'])
    below = sorted((b for b in blocks if b is not title and b['top'] > title['top']), key=lambda b: b['top'])
    sub = below[0] if below else None
    for kind, b in (('TITLE', title), ('SUBTITLE', sub)):
        if b and b['n'] > 1:
            fails += 1
            print(f'page {pno}: {kind} WRAPS ({b["n"]} lines): {b["text"][:80]}')
print('wrapped titles/subtitles:', fails)
sys.exit(1 if fails else 0)
