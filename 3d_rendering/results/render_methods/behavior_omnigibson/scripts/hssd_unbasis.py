"""Rewrite an HSSD glb so tools other than habitat-sim can read its textures.

HSSD-hab glbs store textures as KTX2 with Basis Universal compression (glTF extension
KHR_texture_basisu). Isaac Sim's importers, trimesh and OmniGibson's custom-object import
cannot decode those, so every texture comes out missing. This script transcodes each KTX2
image to PNG with Khronos' `ktx extract --transcode rgba8` (KTX-Software 4.4.2) and writes
a plain glb with PNG images.

Run with the tools venv:
  /mnt/nvme/oliver/robot/render_methods/behavior/tools_venv/bin/python hssd_unbasis.py in.glb out.glb
"""
import os
import subprocess
import sys
import tempfile

import pygltflib

KTX_DIR = "/mnt/nvme/oliver/robot/render_methods/behavior/ktx/KTX-Software-4.4.2-Linux-x86_64"
KTX = os.path.join(KTX_DIR, "bin", "ktx")
ENV = dict(os.environ, LD_LIBRARY_PATH=os.path.join(KTX_DIR, "lib"))


def ktx2_to_png(data: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "t.ktx2"), os.path.join(d, "t.png")
        open(src, "wb").write(data)
        subprocess.run([KTX, "extract", "--transcode", "rgba8", src, dst], check=True, env=ENV,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return open(dst, "rb").read()


def convert(src: str, dst: str) -> int:
    g = pygltflib.GLTF2().load(src)
    blob = bytearray(g.binary_blob() or b"")
    n = 0
    new_blob = bytearray()
    # Rebuild the binary chunk: copy every buffer view, swapping KTX2 images for PNG.
    ktx_views = {img.bufferView for img in g.images if img.mimeType == "image/ktx2" and img.bufferView is not None}
    for i, bv in enumerate(g.bufferViews):
        chunk = bytes(blob[(bv.byteOffset or 0):(bv.byteOffset or 0) + bv.byteLength])
        if i in ktx_views:
            chunk = ktx2_to_png(chunk)
            n += 1
        while len(new_blob) % 4:
            new_blob += b"\0"
        bv.byteOffset = len(new_blob)
        bv.byteLength = len(chunk)
        new_blob += chunk
    for img in g.images:
        if img.mimeType == "image/ktx2":
            img.mimeType = "image/png"
    for t in g.textures:
        ext = (t.extensions or {}).pop("KHR_texture_basisu", None)
        if ext is not None and t.source is None:
            t.source = ext["source"]
    for lst in ("extensionsUsed", "extensionsRequired"):
        v = getattr(g, lst) or []
        setattr(g, lst, [e for e in v if e != "KHR_texture_basisu"])
    g.buffers[0].byteLength = len(new_blob)
    g.set_binary_blob(bytes(new_blob))
    g.save_binary(dst)
    return n


if __name__ == "__main__":
    print(convert(sys.argv[1], sys.argv[2]), "textures transcoded")
