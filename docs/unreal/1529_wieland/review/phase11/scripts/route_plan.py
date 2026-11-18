"""Phase 11, step 11.2: turn a list of legs into one camera route that keeps clear of walls and furniture.

    python -B review/phase11/scripts/route_plan.py <name>

Reads review/phase11/paths/<name>_legs.json = {"clearance": cm, "legs": [leg, ...]} where a leg is either
    {"floor": "1", "via": [[x, y], ...]}          walk on that floor through the points, around what is in the way
    {"stair": [[x, y, z], ...]}                    fixed points on a stair (z is the walking surface there)
    {"free": [[x, y, z], ...]}                     fixed points anywhere (outdoors, through a door)
On a floor it searches the floor map of map_probe.py (cells free at eye height with the walking surface at floor
height), grown by the clearance, for the shortest way between successive points and then straightens it.
Writes review/phase11/paths/<name>_route.json = {"points": [[x, y, floor z], ...]} for path_probe.py.
"""
import heapq
import json
import math
import sys

PATHS = "review/phase11/paths/"
FLOOR_Z = {"L": -152.4, "1": 203.2, "2": 528.3, "3": 853.4, "4": 1178.6, "R": 1524.0}


class Floor:
    def __init__(self, name, clearance):
        data = json.load(open(PATHS + "map_%s.json" % name))
        self.x0, self.y0, self.cell, self.nx, self.ny = data["x0"], data["y0"], data["cell"], data["nx"], data["ny"]
        solid = [[(c[0] >= 0 or c[1] is None or abs(c[1]) > 6.0) for c in row] for row in data["cells"]]
        reach = int(math.ceil(clearance / self.cell))
        self.blocked = [[False] * self.ny for _ in range(self.nx)]
        for i in range(self.nx):
            for j in range(self.ny):
                if solid[i][j]:
                    for a in range(max(0, i - reach), min(self.nx, i + reach + 1)):
                        for b in range(max(0, j - reach), min(self.ny, j + reach + 1)):
                            if (a - i) ** 2 + (b - j) ** 2 <= reach * reach:
                                self.blocked[a][b] = True

    def cell_of(self, x, y):
        return int((x - self.x0) / self.cell), int((y - self.y0) / self.cell)

    def centre(self, i, j):
        return self.x0 + (i + 0.5) * self.cell, self.y0 + (j + 0.5) * self.cell

    def open_at(self, i, j):
        return 0 <= i < self.nx and 0 <= j < self.ny and not self.blocked[i][j]

    def nearest_open(self, i, j):
        if self.open_at(i, j):
            return i, j
        for radius in range(1, 12):
            best = None
            for a in range(i - radius, i + radius + 1):
                for b in range(j - radius, j + radius + 1):
                    if self.open_at(a, b):
                        d = (a - i) ** 2 + (b - j) ** 2
                        if best is None or d < best[0]:
                            best = (d, a, b)
            if best:
                return best[1], best[2]
        raise RuntimeError("no free cell near %s" % ((i, j),))

    def sight(self, a, b):
        steps = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
        for k in range(steps + 1):
            f = k / float(steps)
            if not self.open_at(int(round(a[0] + (b[0] - a[0]) * f)), int(round(a[1] + (b[1] - a[1]) * f))):
                return False
        return True

    def search(self, start, goal):
        frontier = [(0.0, start)]
        cost, parent = {start: 0.0}, {start: None}
        while frontier:
            _, here = heapq.heappop(frontier)
            if here == goal:
                break
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    there = (here[0] + di, here[1] + dj)
                    if not self.open_at(*there):
                        continue
                    new = cost[here] + math.hypot(di, dj)
                    if there not in cost or new < cost[there]:
                        cost[there] = new
                        parent[there] = here
                        heapq.heappush(frontier, (new + math.hypot(goal[0] - there[0], goal[1] - there[1]), there))
        if goal not in parent:
            raise RuntimeError("no way from %s to %s" % (self.centre(*start), self.centre(*goal)))
        chain = []
        here = goal
        while here is not None:
            chain.append(here)
            here = parent[here]
        chain.reverse()
        # straighten: keep a cell only where the straight line from the last kept cell stops being free
        kept = [chain[0]]
        k = 0
        while k < len(chain) - 1:
            far = k + 1
            for m in range(len(chain) - 1, k, -1):
                if self.sight(chain[k], chain[m]):
                    far = m
                    break
            kept.append(chain[far])
            k = far
        return kept


def main():
    name = sys.argv[1]
    job = json.load(open(PATHS + name + "_legs.json"))
    clearance = job.get("clearance", 30.0)
    floors, points = {}, []

    def add(x, y, z):
        if points and math.hypot(points[-1][0] - x, points[-1][1] - y) < 5.0 and abs(points[-1][2] - z) < 5.0:
            return
        points.append([round(x, 1), round(y, 1), round(z, 1)])

    for leg in job["legs"]:
        if "floor" in leg:
            key = (leg["floor"], leg.get("clearance", clearance))
            if key not in floors:
                floors[key] = Floor(*key)
            floor = floors[key]
            z = FLOOR_Z[leg["floor"]]
            via = leg["via"]
            cells = [floor.nearest_open(*floor.cell_of(x, y)) for x, y in via]
            add(via[0][0], via[0][1], z)
            for a, b in zip(cells[:-1], cells[1:]):
                for cell in floor.search(a, b):
                    x, y = floor.centre(*cell)
                    add(x, y, z)
        else:
            for x, y, z in leg.get("stair") or leg["free"]:
                add(x, y, z)
    length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points[:-1], points[1:]))
    json.dump({"points": points}, open(PATHS + name + "_route.json", "w"))
    print(name, len(points), "points, %.1f m in plan" % (length / 100.0))
    for n, p in enumerate(points):
        print(n, p)


main()
