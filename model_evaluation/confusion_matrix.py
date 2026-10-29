"""Confusion matrix for the SSB YOLOv8 model (model.pt) at conf 0.65, in the format of the RSOS FWB matrix.

Sources
  1) SSB validation split (512 px crops, all classes annotated): plain YOLO prediction per crop (needs a GPU,
     `model.pt` and `val/images`, `val/labels` in this folder). If these are missing, the stored
     `assets/model_evaluation/ssb_confusion_validation.csv` is used.
  2) SSB bird test set (full images not used for training, only giant petrels / brown skuas / snowy sheathbills
     annotated; `assets/model_evaluation/bird_testset_*.csv`): predictions of the analysis pipeline (`SSB.csv`).
     For each image, `bird_testset_images.csv` lists the bird classes that were annotated in it.
Matching: per image, class-agnostic greedy matching of annotations and predictions by IoU (>= 0.5).
  matched -> cell [true, predicted]; unmatched annotation -> 'False negative';
  unmatched prediction -> 'False positive' (bird test set: only predictions of the classes annotated in that image).
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ASSETS = ROOT / "assets" / "model_evaluation"
CONF, IOU_MIN = 0.65, 0.5
names = ["elephant seal", "female", "giant petrel", "male", "penguin", "pup", "sheathbill", "skua"]
order = ["male", "female", "pup", "elephant seal", "skua", "giant petrel", "sheathbill", "penguin"]
label = {"male": "Male", "female": "Female", "pup": "Pup", "elephant seal": "Elephant seal", "skua": "Brown skua",
         "giant petrel": "Giant petrel", "sheathbill": "Snowy sheathbill", "penguin": "King penguin"}


def iou(a, b):
    x1 = np.maximum(a[:, None, 0], b[None, :, 0]); y1 = np.maximum(a[:, None, 1], b[None, :, 1])
    x2 = np.minimum(a[:, None, 2], b[None, :, 2]); y2 = np.minimum(a[:, None, 3], b[None, :, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    aa = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1]); ab = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    return inter / (aa[:, None] + ab[None, :] - inter)


def accumulate(cm, gt_cls, gt_box, pr_cls, pr_box, fp_classes=None):
    used_g, used_p = set(), set()
    if len(gt_cls) and len(pr_cls):
        m = iou(np.asarray(gt_box, float), np.asarray(pr_box, float))
        for flat in np.argsort(-m, axis=None):
            g, p = np.unravel_index(flat, m.shape)
            if m[g, p] < IOU_MIN:
                break
            if g in used_g or p in used_p:
                continue
            used_g.add(g); used_p.add(p)
            cm.loc[gt_cls[g], pr_cls[p]] += 1
    for g in range(len(gt_cls)):
        if g not in used_g:
            cm.loc[gt_cls[g], "False negative"] += 1
    for p in range(len(pr_cls)):
        if p not in used_p and (fp_classes is None or pr_cls[p] in fp_classes):
            cm.loc["False positive", pr_cls[p]] += 1


def empty():
    return pd.DataFrame(0, index=order + ["False positive"], columns=order + ["False negative"])


def xyxy(x, y, w, h):
    return np.column_stack([x, y, np.asarray(x) + np.asarray(w), np.asarray(y) + np.asarray(h)]).astype(float)


# ---- 1) validation split
if (HERE / "model.pt").exists() and (HERE / "val" / "images").exists():
    from ultralytics import YOLO
    model = YOLO(str(HERE / "model.pt"))
    cm_val = empty()
    imgs = sorted((HERE / "val" / "images").glob("*.jpg"))
    for i in range(0, len(imgs), 32):
        for res in model.predict(source=[str(f) for f in imgs[i:i + 32]], conf=CONF, imgsz=512, verbose=False):
            f = Path(res.path)
            w, h = res.orig_shape[1], res.orig_shape[0]
            gt_cls, gt_box = [], []
            lab = HERE / "val" / "labels" / (f.stem + ".txt")
            if lab.exists():
                for line in open(lab):
                    if line.strip():
                        c, cx, cy, bw, bh = line.split()[:5]
                        cx, cy, bw, bh = float(cx) * w, float(cy) * h, float(bw) * w, float(bh) * h
                        gt_cls.append(names[int(c)]); gt_box.append([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2])
            accumulate(cm_val, gt_cls, gt_box, [names[int(c)] for c in res.boxes.cls.cpu().numpy()],
                       res.boxes.xyxy.cpu().numpy().tolist())
    cm_val.to_csv(ASSETS / "ssb_confusion_validation.csv")
else:
    cm_val = pd.read_csv(ASSETS / "ssb_confusion_validation.csv", index_col=0)

# ---- 2) bird test set
ann = pd.read_csv(ASSETS / "bird_testset_annotations.csv")
test_imgs = pd.read_csv(ASSETS / "bird_testset_images.csv")
pred = pd.read_csv(ROOT / "SSB.csv", usecols=["filename", "class", "x_px", "y_px", "width_px", "height_px"])
pred = pred[pred.filename.isin(test_imgs.filename)]          # SSB.csv contains detections with conf >= 0.65 only
cm_bird = empty()
for f, annotated in zip(test_imgs.filename, test_imgs.annotated_classes):
    g, p = ann[ann.filename == f], pred[pred.filename == f]
    accumulate(cm_bird, list(g["class"]), xyxy(g.x, g.y, g.width, g.height).tolist(),
               list(p["class"]), xyxy(p.x_px, p.y_px, p.width_px, p.height_px).tolist(),
               fp_classes=set(annotated.split(";")))

cm_all = cm_val + cm_bird
for name, cm in [("birdset", cm_bird), ("combined", cm_all)]:
    cm.to_csv(ASSETS / f"ssb_confusion_{name}.csv")

rows = []
for c in order:
    tp = cm_all.loc[c, c]; true = cm_all.loc[c].sum(); predicted = cm_all[c].sum()
    p_, r_ = (tp / predicted if predicted else np.nan), (tp / true if true else np.nan)
    rows.append(dict(cls=label[c], true_instances=true, TP=tp, precision=p_, recall=r_,
                     F1=2 * p_ * r_ / (p_ + r_) if tp else 0.0))
pd.set_option("display.width", 220)
print(cm_all.to_string())
print(pd.DataFrame(rows).round(2).to_string(index=False))
