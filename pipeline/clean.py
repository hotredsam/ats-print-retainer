"""Load a mesh, keep the largest connected piece, fill small holes, and save it.

Research and visualization only. Not for making anything worn in the mouth.
"""
import sys

import trimesh


def clean(path_in: str, path_out: str) -> None:
    mesh = trimesh.load(path_in, force="mesh")
    parts = mesh.split(only_watertight=False)
    if len(parts) > 1:
        mesh = max(parts, key=lambda m: m.area)
    trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    mesh.export(path_out)
    print(f"faces: {len(mesh.faces)} watertight: {mesh.is_watertight}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: clean.py <in.stl> <out.stl>")
    clean(sys.argv[1], sys.argv[2])
