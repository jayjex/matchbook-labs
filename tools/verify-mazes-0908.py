#!/usr/bin/env python3
"""BFS-verify the 4 SVG mazes in free-printable-mazes.html.

Checks per maze (puzzle SVG + solution SVG):
  1. walls identical between puzzle & solution SVG
  2. cell graph: connected + edges == n*n-1  -> tree -> exactly one path (no loops)
  3. drawn solution path: starts (0,0), ends (n-1,n-1), every consecutive
     pair is adjacent with NO wall between, no repeated cells
  4. BFS path (unique, since tree) == drawn path
  5. step count matches the claimed number
"""
import re, sys, collections

HTML = "free-printable-mazes.html"
CLAIMS = {9: 36, 11: 68, 12: 80, 13: 46}
OFF = 6.0
CELL = 22.0

html = open(HTML).read()

# split: 4 puzzle SVGs (before Solutions h2) + 4 solution SVGs (inside <details>)
main, solpart = html.split('<h2 class="noprint">Solutions</h2>', 1)
puzzle_svgs = re.findall(r'<svg class="maze".*?</svg>', main, re.S)
sol_svgs = re.findall(r'<svg class="maze".*?</svg>', solpart, re.S)
assert len(puzzle_svgs) == 4, f"expected 4 puzzle svgs, got {len(puzzle_svgs)}"
assert len(sol_svgs) == 4, f"expected 4 solution svgs, got {len(sol_svgs)}"

def parse(svg):
    label = re.search(r'aria-label="(\d+)x(\d+)', svg)
    n = int(label.group(1))
    assert int(label.group(2)) == n
    # interior walls only (stroke-width 1.4)
    walls_v, walls_h = set(), set()  # (col,row) = wall right of cell / below cell
    for m in re.finditer(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)" stroke="#58a6ff" stroke-width="1.4"', svg):
        x1, y1, x2, y2 = map(float, m.groups())
        if abs(x1 - x2) < 0.01:  # vertical wall
            x = x1
            ya, yb = sorted((y1, y2))
            k = round((x - OFF) / CELL)
            r0, r1 = round((ya - OFF) / CELL), round((yb - OFF) / CELL)
            for r in range(r0, r1):
                walls_v.add((k - 1, r))  # between col k-1 and col k, row r
        elif abs(y1 - y2) < 0.01:
            y = y1
            xa, xb = sorted((x1, x2))
            k = round((y - OFF) / CELL)
            c0, c1 = round((xa - OFF) / CELL), round((xb - OFF) / CELL)
            for c in range(c0, c1):
                walls_h.add((c, k - 1))  # between row k-1 and row k, col c
        else:
            raise AssertionError(f"diagonal wall {m.group(0)[:60]}")
    pts = []
    dmatch = re.search(r'<path d="([^"]+)"', svg)
    if dmatch:
        d = dmatch.group(1)
        for m in re.finditer(r'([\d.]+) ([\d.]+)', d):
            x, y = float(m.group(1)), float(m.group(2))
            pts.append((round((x - OFF - CELL / 2) / CELL), round((y - OFF - CELL / 2) / CELL)))
    return n, walls_v, walls_h, pts

def neighbors(n, walls_v, walls_h):
    nb = {}
    for c in range(n):
        for r in range(n):
            out = []
            if c > 0 and (c - 1, r) not in walls_v: out.append((c - 1, r))
            if c < n - 1 and (c, r) not in walls_v: out.append((c + 1, r))
            if r > 0 and (c, r - 1) not in walls_h: out.append((c, r - 1))
            if r < n - 1 and (c, r) not in walls_h: out.append((c, r + 1))
            nb[(c, r)] = out
    return nb

def bfs_path(n, nb, start, end):
    prev = {start: None}
    q = collections.deque([start])
    while q:
        cur = q.popleft()
        if cur == end: break
        for nxt in nb[cur]:
            if nxt not in prev:
                prev[nxt] = cur
                q.append(nxt)
    assert end in prev, f"no BFS path {start}->{end}"
    path, cur = [], end
    while cur is not None:
        path.append(cur); cur = prev[cur]
    return path[::-1]

ok = True
for i, (psvg, ssvg) in enumerate(zip(puzzle_svgs, sol_svgs), 1):
    n, pv, ph, ppts = parse(psvg)
    n2, sv, sh, spts = parse(ssvg)
    assert not ppts and spts, f"maze {i}: expected no path on puzzle svg, path on solution svg"
    assert n == n2 == list(CLAIMS)[i - 1], f"maze {i}: size {n} unexpected"
    if (pv, ph) != (sv, sh):
        ok = False; print(f"maze {i} ({n}x{n}): WALLS DIFFER between puzzle and solution svg"); continue
    nb = neighbors(n, pv, ph)
    edges = sum(len(v) for v in nb.values()) // 2
    # connectivity
    seen, q = {(0, 0)}, collections.deque([(0, 0)])
    while q:
        cur = q.popleft()
        for nxt in nb[cur]:
            if nxt not in seen: seen.add(nxt); q.append(nxt)
    conn = len(seen) == n * n
    tree = edges == n * n - 1
    if not (conn and tree):
        ok = False
        print(f"maze {i} ({n}x{n}): FAIL connected={conn} ({len(seen)}/{n*n}) edges={edges} vs {n*n-1} (tree={tree})")
        continue
    path = bfs_path(n, nb, (0, 0), (n - 1, n - 1))
    steps = len(path) - 1
    # drawn path checks (solution svg only)
    ppts = spts
    draw_ok = ppts[0] == (0, 0) and ppts[-1] == (n - 1, n - 1)
    draw_ok = draw_ok and len(set(ppts)) == len(ppts)
    for a, b in zip(ppts, ppts[1:]):
        if b not in nb[a]:
            draw_ok = False
            print(f"maze {i}: drawn path crosses wall {a}->{b}")
            break
    match = ppts == path
    claimed = CLAIMS[n]
    status = "PASS" if (draw_ok and match and steps == claimed) else "FAIL"
    if status == "FAIL": ok = False
    print(f"maze {i} ({n}x{n}): {status} tree={tree} connected={conn} unique_path={match} "
          f"bfs_steps={steps} claimed={claimed} drawn_steps={len(ppts)-1} start={ppts[0]} end={ppts[-1]}")

print("ALL PASS" if ok else "SOME FAIL")
sys.exit(0 if ok else 1)
