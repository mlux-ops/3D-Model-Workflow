"""Phase 9, step 9.1: mean of chosen columns of the engine's CSV profiles (packed copies in a profile's csv folder).

    python -B csv_breakdown.py <csv.gz> [<csv.gz> ...]
"""
import csv, gzip, sys

KEEP = ("FrameTime", "GPUTime", "RenderThreadTime", "GameThreadTime", "RHIThreadTime", "RHI/DrawCalls", "RHI/PrimitivesDrawn",
        "GPUMem/LocalUsedMB", "LightCount/All", "LightCount/UpdatedShadowMaps", "ShadowCacheUsageMB", "GPUSceneInstanceCount",
        "RayTracingGeometry/TotalResidentSizeMB", "TextureStreaming/StreamingPool", "TextureStreaming/WantedMips",
        "TextureStreaming/NonStreamingMips", "RenderTargetPoolSize", "NaniteStreaming/RootAllocationMB", "RDGCount/Passes")
PREFIX = ("DrawCall/", "Exclusive/RenderThread/", "Exclusive/GameThread/")


def read(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
        rows = list(csv.reader(handle))
    header = [r for r in rows if "FrameTime" in r][-1]
    ft = header.index("FrameTime")
    out = {}
    for i, name in enumerate(header):
        if name in KEEP or name.startswith(PREFIX):
            vals = []
            for r in rows:
                if "FrameTime" in r or len(r) <= max(i, ft):
                    continue
                try:
                    if float(r[ft]) > 0:
                        vals.append(float(r[i]))
                except ValueError:
                    pass
            if vals:
                out[name] = (sum(vals) / len(vals), max(vals))
    return out


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print("==", path)
        data = read(path)
        for name in sorted(data, key=lambda n: (not n in KEEP, -data[n][0])):
            mean, worst = data[name]
            if name in KEEP or mean >= 0.15:
                print("  %-58s mean %10.2f  max %10.2f" % (name, mean, worst))
