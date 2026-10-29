# Evaluation of the SSB detection model

`confusion_matrix.py` computes the confusion matrix of the SSB YOLOv8 model (`model.pt`) at the confidence
threshold used in the analysis (0.65; detections matched to annotations at IoU ≥ 0.5). Its output is stored in
`assets/model_evaluation/` and read by `analysis.ipynb` (Supplementary Figures 1 and 6, Supplementary Table 1).

The matrix combines two sources:
* **Validation split** of the training data (512 px crops, all classes annotated; see `training.ipynb`). Predicting
  these crops needs a GPU, `model.pt` and the crops in `val/images`, `val/labels` in this folder. If they are missing,
  the stored `assets/model_evaluation/ssb_confusion_validation.csv` is used.
* **Bird test set**: full-size SSB images not used for training, in which only giant petrels, brown skuas and snowy
  sheathbills were annotated (`assets/model_evaluation/bird_testset_annotations.csv`;
  `bird_testset_images.csv` lists which bird classes were annotated in each image). The predictions are taken from
  `SSB.csv` (Zenodo), i.e. from the same pipeline as the analysed images. This part runs on a normal computer.

```bash
python model_evaluation/confusion_matrix.py
```

| Output (`assets/model_evaluation/`) | Content |
|---|---|
| `ssb_confusion_validation.csv` | Validation crops |
| `ssb_confusion_birdset.csv` | Bird test set |
| `ssb_confusion_combined.csv` | Sum of both (used in `analysis.ipynb`) |
