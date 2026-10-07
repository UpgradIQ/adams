def lum(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def ratio(fg, bg):
    a, b = sorted([lum(fg), lum(bg)], reverse=True)
    return (a + 0.05) / (b + 0.05)

if __name__ == '__main__':
    import sys
    # usage: python3 contrast.py FG BG [FG BG ...]   (hex colors); exit 1 if any pair is below 4.5
    a = sys.argv[1:]
    bad = 0
    for fg, bg in zip(a[::2], a[1::2]):
        r = ratio(fg, bg); ok = r >= 4.5; bad += not ok
        print(f'{fg} on {bg}: {r:.2f}:1', 'OK' if ok else 'FAIL')
    sys.exit(1 if bad or len(a) < 2 or len(a) % 2 else 0)
