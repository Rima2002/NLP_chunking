# Nested Chunking Degerlendirme Raporu

Bu rapor `python src/evaluate.py` komutu ile otomatik uretilir.
Projede istatistiksel makine ogrenmesi yontemi olarak Conditional Random Fields (CRF) kullanilmistir.

## Veri ve Isaretleme Formati

- Tum isaretlemeler CoNLL formatindadir.
- Sutunlar: `ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE`.
- `B` etiketi isaretlemenin baslangicini, `I` etiketi devamini gosterir.
- `_` ic chunk bulunmadigini, `O` ilgili hedef icin disarida kalan tokeni gosterir.
- Test cumlesi sayisi: `12`.
- Test token sayisi: `74`.

## Modelleme

Ayni ozelliklerle uc ayri CRF modeli egitilmistir: `outer_model.pkl`, `inner_model.pkl` ve `clause_model.pkl`.
Boylece dis obek, ic obek ve cumlecik sinirlari birbirinden bagimsiz raporlanabilir.

## Sonuclar

Precision, recall, f-measure ve accuracy degerleri `outputs` klasorune rapor olarak kaydedilir.
Confusion matrix sonuclari PNG grafik dosyasi olarak uretilir.

### Genel Basari Ozeti

| Hedef sutun | Accuracy | Rapor dosyasi | Confusion matrix grafigi |
|---|---:|---|---|
| CHUNK-OUTER | 0.8784 | outer_classification_report.txt | outer_confusion_matrix.png |
| CHUNK-INNER | 0.9189 | inner_classification_report.txt | inner_confusion_matrix.png |
| CLAUSE | 0.8919 | clause_classification_report.txt | clause_confusion_matrix.png |

### Confusion Matrix Grafik Ozeti

Asagidaki gorsel uc hedef sutunun karisiklik matrislerini grafik olarak birlikte gosterir.

![Tum confusion matrix grafikleri](all_confusion_matrices.png)

### CHUNK-OUTER

Dis obekleri gosterir. NP, VP, ADVP ve O etiketleri kullanilir.

- Accuracy: `0.8784`
- Ayrintili metin raporu: `outer_classification_report.txt`
- Confusion matrix grafigi: `outer_confusion_matrix.png`

![CHUNK-OUTER confusion matrix](outer_confusion_matrix.png)

| Sinif | Precision | Recall | F-measure | Support |
|---|---:|---:|---:|---:|
| B-ADVP | 0.7000 | 0.8750 | 0.7778 | 8 |
| B-NP | 0.9048 | 0.7600 | 0.8261 | 25 |
| B-VP | 0.9333 | 0.9333 | 0.9333 | 15 |
| I-ADVP | 1.0000 | 0.6667 | 0.8000 | 3 |
| I-NP | 0.7500 | 1.0000 | 0.8571 | 9 |
| I-VP | 1.0000 | 1.0000 | 1.0000 | 2 |
| O | 1.0000 | 1.0000 | 1.0000 | 12 |
| Macro avg | 0.8983 | 0.8907 | 0.8849 | 74 |
| Weighted avg | 0.8915 | 0.8784 | 0.8782 | 74 |

Confusion matrix sayisal tablo:

| Gercek \ Tahmin | B-ADVP | B-NP | B-VP | I-ADVP | I-NP | I-VP | O |
|---|---:|---:|---:|---:|---:|---:|---:|
| B-ADVP | 7 | 1 | 0 | 0 | 0 | 0 | 0 |
| B-NP | 3 | 19 | 1 | 0 | 2 | 0 | 0 |
| B-VP | 0 | 1 | 14 | 0 | 0 | 0 | 0 |
| I-ADVP | 0 | 0 | 0 | 2 | 1 | 0 | 0 |
| I-NP | 0 | 0 | 0 | 0 | 9 | 0 | 0 |
| I-VP | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| O | 0 | 0 | 0 | 0 | 0 | 0 | 12 |

### CHUNK-INNER

Dis obek icindeki ic yapilari gosterir. Bu projede RELCL ve bos ic obek icin _ kullanilir.

- Accuracy: `0.9189`
- Ayrintili metin raporu: `inner_classification_report.txt`
- Confusion matrix grafigi: `inner_confusion_matrix.png`

![CHUNK-INNER confusion matrix](inner_confusion_matrix.png)

| Sinif | Precision | Recall | F-measure | Support |
|---|---:|---:|---:|---:|
| B-RELCL | 0.5000 | 0.3333 | 0.4000 | 6 |
| I-RELCL | 0.6000 | 1.0000 | 0.7500 | 3 |
| _ | 0.9692 | 0.9692 | 0.9692 | 65 |
| Macro avg | 0.6897 | 0.7675 | 0.7064 | 74 |
| Weighted avg | 0.9162 | 0.9189 | 0.9142 | 74 |

Confusion matrix sayisal tablo:

| Gercek \ Tahmin | B-RELCL | I-RELCL | _ |
|---|---:|---:|---:|
| B-RELCL | 2 | 2 | 2 |
| I-RELCL | 0 | 3 | 0 |
| _ | 2 | 0 | 63 |

### CLAUSE

Cumlecikleri gosterir. RELCL, COMPCL ve cumlecik disi O etiketleri kullanilir.

- Accuracy: `0.8919`
- Ayrintili metin raporu: `clause_classification_report.txt`
- Confusion matrix grafigi: `clause_confusion_matrix.png`

![CLAUSE confusion matrix](clause_confusion_matrix.png)

| Sinif | Precision | Recall | F-measure | Support |
|---|---:|---:|---:|---:|
| B-COMPCL | 1.0000 | 0.3333 | 0.5000 | 3 |
| B-RELCL | 0.5000 | 0.3333 | 0.4000 | 6 |
| I-COMPCL | 1.0000 | 1.0000 | 1.0000 | 1 |
| I-RELCL | 0.6000 | 1.0000 | 0.7500 | 3 |
| O | 0.9365 | 0.9672 | 0.9516 | 61 |
| Macro avg | 0.8073 | 0.7268 | 0.7203 | 74 |
| Weighted avg | 0.8909 | 0.8919 | 0.8811 | 74 |

Confusion matrix sayisal tablo:

| Gercek \ Tahmin | B-COMPCL | B-RELCL | I-COMPCL | I-RELCL | O |
|---|---:|---:|---:|---:|---:|
| B-COMPCL | 1 | 0 | 0 | 0 | 2 |
| B-RELCL | 0 | 2 | 0 | 2 | 2 |
| I-COMPCL | 0 | 0 | 1 | 0 | 0 |
| I-RELCL | 0 | 0 | 0 | 3 | 0 |
| O | 0 | 2 | 0 | 0 | 59 |

## Tahmin Dosyasi

`nested_predictions.conll` dosyasinda her token icin altin ve tahmin edilen etiketler birlikte verilir:

```text
ID FORM GOLD_OUTER PRED_OUTER GOLD_INNER PRED_INNER GOLD_CLAUSE PRED_CLAUSE
```
