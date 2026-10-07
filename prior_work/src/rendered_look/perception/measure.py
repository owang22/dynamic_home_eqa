"""Goal 3: how well does real perception do on our pictures, measured in three
separate numbers.

    /home/oliver/miniconda3/bin/python -m rendered_look.perception.measure --rig raised

1. Detection. An open-vocabulary detector (OWLv2) is asked for each kind of
   thing by name. A stored sighting counts as detected when a box for that kind
   overlaps the true box by at least half. Reported by how many pixels the thing
   has, and per kind. False alarms are counted on pictures with none of the
   things in them.

2. Telling look-alikes apart. The true box is cropped and embedded (DINOv2 and
   SigLIP); the crop is matched against reference pictures of every model of
   the same kind (the four-view renders). Right when the nearest reference is
   the thing's own model. The two tablets are the same model in two poses, so
   they are the control that should sit at chance.

3. A vision-language model's choice: not in this script yet.

Nothing here reads the simulator's names during matching: the crop and the
reference pictures are all a model sees. The true box comes from the render
and is the upper bound a perfect detector would give.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random

import numpy as np
import torch
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[3]
HOME = REPO / "results/rendered_look/hh_s151"
TAGS = REPO / "results/rendered_look/object_tags"
KIND_WORDS = {"mug": "a mug", "glass": "a drinking glass", "towel": "a folded towel", "book": "a book",
              "water_bottle": "a water bottle", "razor": "a razor", "charger": "a phone charger",
              "notebook": "a notebook", "tablet": "a tablet computer", "glasses": "a pair of glasses",
              "medication": "a pill bottle"}
BINS = [(200, 400), (400, 1000), (1000, 3000), (3000, 10 ** 9)]


def kind_of(thing: str) -> str:
    return thing.rsplit("_", 1)[0]


def iou(a, b) -> float:
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter + 1e-9)


def load_sightings(rig_dir: pathlib.Path, moments_wanted: int, rng: random.Random):
    """Frames with at least one asked-about thing in view (200 px, not cut), and empty frames."""
    moments = {m["t"]: m for m in json.load((rig_dir / "moments.json").open())}
    ts = sorted(moments)
    keep = set(rng.sample(ts, min(moments_wanted, len(ts))))
    with_things, empty = [], []
    with (rig_dir / "observations.jsonl").open() as rows:
        for line in rows:
            row = json.loads(line)
            if row["t"] not in keep:
                continue
            things = [p for p in row["in_picture"] if not p["is_person"] and p["pixels"] >= 200 and not p.get("cut_by_the_edge")]
            (with_things if things else empty).append((row, things))
    return with_things, empty


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rig", default="raised")
    parser.add_argument("--moments", type=int, default=60, help="how many of the 248 question times to sample")
    parser.add_argument("--empty-frames", type=int, default=300)
    args = parser.parse_args()
    rng = random.Random(0)
    rig_dir = HOME / "searchbench" / args.rig
    frames, empty = load_sightings(rig_dir, args.moments, rng)
    empty = rng.sample(empty, min(args.empty_frames, len(empty)))
    print(f"{len(frames)} pictures with things, {len(empty)} empty pictures, from {args.moments} moments")
    device = "cuda"

    # ------------------------------------------------------------------ 1. detection
    from transformers import Owlv2ForObjectDetection, Owlv2Processor
    processor = Owlv2Processor.from_pretrained("google/owlv2-base-patch16-ensemble")
    detector = Owlv2ForObjectDetection.from_pretrained("google/owlv2-base-patch16-ensemble").to(device).eval()
    kinds = list(KIND_WORDS)
    queries = [KIND_WORDS[k] for k in kinds]
    thresholds = [0.1, 0.2, 0.3]

    def detect(image: Image.Image):
        inputs = processor(text=[queries], images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            out = detector(**inputs)
        # OWLv2 pads the image to a square; boxes come back in that square's frame
        side = max(image.size)
        result = processor.post_process_grounded_object_detection(out, threshold=min(thresholds), text_labels=[queries],
                                                         target_sizes=torch.tensor([[side, side]]))[0]
        w, h = image.size
        boxes = result["boxes"].cpu().numpy() / np.array([w, h, w, h])   # back to the picture's own frame
        return [(kinds[int(l)], float(s), [float(v) for v in b])
                for b, s, l in zip(boxes, result["scores"].cpu().numpy(), result["labels"].cpu().numpy())]

    per_bin = {th: collections.Counter() for th in thresholds}
    per_kind = {th: collections.Counter() for th in thresholds}
    totals_bin, totals_kind = collections.Counter(), collections.Counter()
    crops = []   # for matching: (thing, kind, pixels, crop image, moment, place)
    distinct_frames = len({row["frame"] for row, _ in frames})
    distinct_triples = collections.defaultdict(set)   # kind -> {(thing, place-ish, t)}
    for n, (row, things) in enumerate(frames):
        image = Image.open(rig_dir / "frames" / row["frame"]).convert("RGB")
        w, h = image.size
        found = detect(image)
        for p in things:
            kind, b = kind_of(p["what"]), p["box"]
            # the stored box is in the render's frame (960 wide); the saved picture keeps the aspect ratio
            truth = [b[0], b[1], b[2], b[3]]
            bin_name = next(f"{lo}-{hi if hi < 10**9 else ''}" for lo, hi in BINS if lo <= p["pixels"] < hi)
            totals_bin[bin_name] += 1
            totals_kind[kind] += 1
            distinct_triples[kind].add((p["what"], row["position"].split("#")[0], row["t"]))
            for th in thresholds:
                hit = any(k == kind and s >= th and iou(box, truth) >= 0.5 for k, s, box in found)
                per_bin[th][bin_name] += hit
                per_kind[th][kind] += hit
            if p["pixels"] >= 400:
                pad = 0.1
                x0, y0 = max(0, (b[0] - pad * (b[2] - b[0])) * w), max(0, (b[1] - pad * (b[3] - b[1])) * h)
                x1, y1 = min(w, (b[2] + pad * (b[2] - b[0])) * w), min(h, (b[3] + pad * (b[3] - b[1])) * h)
                crops.append((p["what"], kind, p["pixels"], image.crop((int(x0), int(y0), int(x1), int(y1))), row["t"], row["position"].split("#")[0]))
        if n % 200 == 0:
            print(f"  detection: picture {n} of {len(frames)}", flush=True)
    false_alarms = {th: 0 for th in thresholds}
    for row, _ in empty:
        found = detect(Image.open(rig_dir / "frames" / row["frame"]).convert("RGB"))
        for th in thresholds:
            false_alarms[th] += sum(1 for k, s, box in found if s >= th)
    detection = {
        "detector": "google/owlv2-base-patch16-ensemble", "queries": KIND_WORDS, "sightings": sum(totals_bin.values()),
        "recall_by_pixels": {th: {b: [per_bin[th][b], totals_bin[b]] for b in totals_bin} for th in thresholds},
        "recall_by_kind": {th: {k: [per_kind[th][k], totals_kind[k]] for k in totals_kind} for th in thresholds},
        "false_alarms_per_empty_picture": {th: false_alarms[th] / max(1, len(empty)) for th in thresholds},
        "empty_pictures": len(empty), "distinct_empty_frames": len({row["frame"] for row, _ in empty}),
        "distinct_frames_with_things": distinct_frames,
        "distinct_thing_place_moment_by_kind": {k: len(v) for k, v in distinct_triples.items()},
        "false_alarm_note": "An upper bound on hallucination: an audit found most of these boxes sit on a tracked thing "
                            "that was too small or cut by the edge to count, or on an untracked object of the home "
                            "(a book on a bookshelf, a towel on a pillow).",
    }
    del detector
    torch.cuda.empty_cache()

    # ------------------------------------------------------------------ 2. look-alikes
    import timm
    import open_clip
    key = json.load((TAGS / "key.json").open())
    tags = json.load((TAGS / "tags.json").open())
    models_of_kind = collections.defaultdict(list)
    references = {}   # model id -> [PIL crops of its four views]
    for obj, info in key.items():
        sheet = Image.open(TAGS / "views" / f"{obj}.png").convert("RGB")
        views = [sheet.crop((x, y, x + 420, y + 420)) for x, y in ((0, 0), (420, 0), (0, 420), (420, 420))]
        references[info["model"]] = views
        models_of_kind[info["class"]].append(info["model"])
    which = json.load((REPO / "results/rendered_look/asked_about_models/which_model_each_object_gets.json").open())["hh_s151_t03"]

    dino = timm.create_model("vit_large_patch14_reg4_dinov2.lvd142m", pretrained=True, num_classes=0).to(device).eval()
    dino_cfg = timm.data.resolve_data_config({}, model=dino)
    dino_tf = timm.data.create_transform(**dino_cfg)
    siglip, _, siglip_tf = open_clip.create_model_and_transforms("ViT-SO400M-14-SigLIP-384", pretrained="webli")
    siglip = siglip.to(device).eval()

    # V-JEPA 2 (ViT-L, 300M), the video encoder, fed a still picture repeated as a short clip;
    # the embedding is the mean of its patch tokens. V-JEPA 2.1 is not on the model hub here.
    from transformers import AutoModel, AutoVideoProcessor
    vjepa = AutoModel.from_pretrained("facebook/vjepa2-vitl-fpc64-256").to(device).eval()
    vjepa_proc = AutoVideoProcessor.from_pretrained("facebook/vjepa2-vitl-fpc64-256")

    def embed(images, which_model):
        with torch.no_grad():
            if which_model == "dinov2":
                x = torch.stack([dino_tf(im) for im in images]).to(device)
                f = dino(x)
            elif which_model == "vjepa2":
                clips = [np.stack([np.asarray(im.convert("RGB").resize((256, 256)))] * 16) for im in images]
                x = vjepa_proc(clips, return_tensors="pt")["pixel_values_videos"].to(device)
                f = vjepa(pixel_values_videos=x).last_hidden_state.mean(dim=1)
            else:
                x = torch.stack([siglip_tf(im) for im in images]).to(device)
                f = siglip.encode_image(x)
        return torch.nn.functional.normalize(f.float(), dim=-1).cpu().numpy()

    # the models actually in this household, by kind: what a search must choose between
    in_house = collections.defaultdict(set)
    for thing, given in which.items():
        in_house[given["class"]].add(given["model"])
    majority = {k: max(collections.Counter(c[0] for c in crops if c[1] == k).values()) / max(1, sum(1 for c in crops if c[1] == k))
                for k in {c[1] for c in crops}}
    matching = {}
    for name in ("dinov2", "siglip", "vjepa2"):
        ref = {m: embed(v, name) for m, v in references.items()}
        right = collections.Counter(); total = collections.Counter()
        right_house = collections.Counter(); total_house = collections.Counter()
        right_all = collections.Counter(); right_kind_all = collections.Counter()
        right_bin = collections.Counter(); total_bin = collections.Counter()
        distinct = collections.defaultdict(set)
        for i in range(0, len(crops), 64):
            batch = crops[i:i + 64]
            feats = embed([c[3] for c in batch], name)
            for (thing, kind, pixels, _, t, place), f in zip(batch, feats):
                own = which[thing]["model"]
                scores_all = {m: float((ref[m] @ f).max()) for m in ref}
                nearest_all = max(scores_all, key=scores_all.get)
                candidates = models_of_kind[kind]
                if len(candidates) >= 2:
                    ok = max(candidates, key=scores_all.get) == own
                    total[kind] += 1; right[kind] += ok
                    bin_name = next(f"{lo}-{hi if hi < 10**9 else ''}" for lo, hi in BINS if lo <= pixels < hi)
                    total_bin[bin_name] += 1; right_bin[bin_name] += ok
                house = sorted(in_house[kind])
                if len(house) >= 2:
                    total_house[kind] += 1
                    right_house[kind] += max(house, key=scores_all.get) == own
                right_all[kind] += nearest_all == own
                right_kind_all[kind] += key[next(o for o, i_ in key.items() if i_["model"] == nearest_all)]["class"] == kind
                distinct[kind].add((thing, place, t))
        matching[name] = {"right_by_kind": {k: [right[k], total[k]] for k in total},
                          "right_by_pixels": {b: [right_bin[b], total_bin[b]] for b in total_bin},
                          "chance_by_kind": {k: 1 / len(models_of_kind[k]) for k in total},
                          "majority_guess_by_kind": {k: round(majority[k], 3) for k in total},
                          "right_among_this_households_models": {k: [right_house[k], total_house[k]] for k in total_house},
                          "right_among_all_24_models": {k: [right_all[k], sum(1 for c in crops if c[1] == k)] for k in right_all},
                          "right_kind_among_all_24_models": {k: [right_kind_all[k], sum(1 for c in crops if c[1] == k)] for k in right_kind_all},
                          "distinct_thing_place_moment_by_kind": {k: len(v) for k, v in distinct.items()}}
    out = {"rig": args.rig, "moments_sampled": args.moments, "empty_frames_asked": args.empty_frames,
           "detection": detection, "matching": matching, "crops_matched": len(crops),
           "note": "The true box is used for cropping, so matching is measured on its own, apart from detection. "
                   "'Right among this household's models' is what a search must decide (two things of a kind here); "
                   "'majority guess' is the score of always naming the commonest thing of that kind, the trivial baseline. "
                   "Counts are of sightings; many pictures repeat, so 'distinct thing, place, moment' is the honest sample size. "
                   "This household has no two identical things, so the control that should sit at chance could not be run."}
    (rig_dir / "perception.json").write_text(json.dumps(out, indent=1))
    print("\ndetection recall by pixels (threshold 0.2):",
          {b: f"{v[0]}/{v[1]}" for b, v in detection["recall_by_pixels"][0.2].items()})
    print("false alarms per empty picture:", detection["false_alarms_per_empty_picture"])
    for name, m in matching.items():
        print(f"{name} right among same-kind models:", {k: f"{v[0]}/{v[1]} (chance {m['chance_by_kind'][k]:.2f})" for k, v in m["right_by_kind"].items()})


if __name__ == "__main__":
    main()
