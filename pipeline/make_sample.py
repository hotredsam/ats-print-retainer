"""Write a synthetic, made-up dental arch mesh for testing the pipeline.

The shape is a closed tube that follows a U-shaped curve, roughly the size of
an arch (millimeters). It is not a real scan of anyone. Pure Python, so it runs
before any dependency is installed.

Usage: python3 pipeline/make_sample.py samples/synthetic_arch.stl
"""
import math
import struct
import sys

ARCH_WIDTH = 50.0   # mm across the open end of the U
ARCH_DEPTH = 40.0   # mm from the open end to the front of the U
TUBE_RADIUS = 4.0   # mm
ALONG = 48          # rings along the curve
AROUND = 16         # vertices per ring


def curve(t: float):
    """Point and tangent on the U, t from 0 to 1."""
    x = (t - 0.5) * ARCH_WIDTH
    y = ARCH_DEPTH * (1 - (2 * t - 1) ** 2)
    dx = ARCH_WIDTH
    dy = ARCH_DEPTH * -4 * (2 * t - 1)
    n = math.hypot(dx, dy)
    return (x, y, 0.0), (dx / n, dy / n, 0.0)


def rings():
    out = []
    for i in range(ALONG):
        (px, py, pz), (tx, ty, _) = curve(i / (ALONG - 1))
        # Side vector in the XY plane, and Z up, span the ring.
        sx, sy = -ty, tx
        ring = []
        for j in range(AROUND):
            a = 2 * math.pi * j / AROUND
            c, s = math.cos(a) * TUBE_RADIUS, math.sin(a) * TUBE_RADIUS
            ring.append((px + sx * c, py + sy * c, pz + s))
        out.append(ring)
    return out


def triangles():
    rs = rings()
    tris = []
    for i in range(ALONG - 1):
        a, b = rs[i], rs[i + 1]
        for j in range(AROUND):
            k = (j + 1) % AROUND
            tris.append((a[j], b[j], b[k]))
            tris.append((a[j], b[k], a[k]))
    # Caps close both ends so the mesh is watertight.
    for ring, flip in ((rs[0], True), (rs[-1], False)):
        cx = sum(p[0] for p in ring) / AROUND
        cy = sum(p[1] for p in ring) / AROUND
        cz = sum(p[2] for p in ring) / AROUND
        for j in range(AROUND):
            k = (j + 1) % AROUND
            tri = ((cx, cy, cz), ring[k], ring[j]) if flip else ((cx, cy, cz), ring[j], ring[k])
            tris.append(tri)
    return tris


def normal(t):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / n, ny / n, nz / n


def write_stl(path: str) -> int:
    tris = triangles()
    with open(path, "wb") as f:
        f.write(b"synthetic arch, not a real scan".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            f.write(struct.pack("<3f", *normal(t)))
            for p in t:
                f.write(struct.pack("<3f", *p))
            f.write(b"\0\0")
    return len(tris)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: make_sample.py <out.stl>")
    print(f"wrote {write_stl(sys.argv[1])} triangles to {sys.argv[1]}")
