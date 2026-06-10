# Turkce Nested Chunking Projesi

Bu proje Turkce cumlelerde nested chunking, yani ic ice gecen isim obekleri
(NP), eylem obekleri (VP), zarf obekleri (ADVP), ilgi cumlecikleri (RELCL) ve
tumlec cumleciklerini (COMPCL) etiketlemek icin hazirlanmistir. Veri 5 sutunlu
CoNLL bicimindedir ve her token icin uc ayri hedef etiket tutulur:
`CHUNK-OUTER`, `CHUNK-INNER` ve `CLAUSE`.

## Veri Formati

`data/train.conll` ve `data/test.conll` dosyalari su sutunlari kullanir:

```text
ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE
```

Cumleler bos satirla ayrilir. `_` etiketi ic chunk olmadigini, `O` etiketi ise
ilgili tokenin chunk veya cumlecik disinda kaldigini gosterir.

Ornek:

```text
1 Dun B-ADVP _ O
2 aksam I-ADVP _ O
3 toplantidan B-NP B-RELCL B-RELCL
4 erken I-NP I-RELCL I-RELCL
5 cikan I-NP I-RELCL I-RELCL
6 ogrencinin I-NP _ O
```

## Etiket Sutunlari

`CHUNK-OUTER`: Dis chunk etiketidir. Bu projede `NP`, `VP`, `ADVP` ve `O`
yapilari kullanilir. BIO bicimiyle `B-NP`, `I-NP`, `B-VP`, `I-VP`,
`B-ADVP`, `I-ADVP` ve `O` etiketleri bulunur.

`CHUNK-INNER`: Dis chunk icindeki ic obek etiketidir. Bu veri setinde ozellikle
ilgi cumlecikleri `B-RELCL` ve `I-RELCL` olarak isaretlenir. Ic chunk yoksa `_`
kullanilir.

`CLAUSE`: Cumlecik sinirlarini gosterir. Ilgi cumlecikleri `B-RELCL` /
`I-RELCL`, tumlec cumlecikleri `B-COMPCL` / `I-COMPCL` olarak etiketlenir.
Cumlecik disinda kalan tokenlar `O` alir.

## Modelleme

Proje isterlerinde izin verilen istatistiksel makine ogrenmesi yontemlerinden
Conditional Random Fields (CRF) secilmistir. Sistem `sklearn-crfsuite`
kutuphanesindeki CRF modelini kullanir. Ayni token ozellikleriyle uc ayri CRF
modeli egitilir:

- `outputs/outer_model.pkl`: `CHUNK_OUTER` tahmini
- `outputs/inner_model.pkl`: `CHUNK_INNER` tahmini
- `outputs/clause_model.pkl`: `CLAUSE` tahmini

Ozellikler arasinda kelime, kucuk harf bicimi, ilk/son 2 ve 3 karakter,
kelime uzunlugu, buyuk harfle baslama, tamamen buyuk olma, rakam ve noktalama
bilgisi, onceki/sonraki kelime bilgileri ile cumle basi/sonu bilgisi vardir.

## Kurulum

```bash
pip install -r requirements.txt
```

## Egitim

```bash
python src/train.py
```

Bu komut `data/train.conll` dosyasini yukler, uc CRF modelini egitir ve
modelleri `outputs` klasorune kaydeder. Egitim sonunda her model icin kullanilan
etiketler terminalde yazdirilir.

## Degerlendirme

```bash
python src/evaluate.py
```

Degerlendirme `data/test.conll` uzerinde uc modeli ayri ayri calistirir ve su
ciktilari uretir:

- `outputs/outer_classification_report.txt`
- `outputs/inner_classification_report.txt`
- `outputs/clause_classification_report.txt`
- `outputs/outer_confusion_matrix.png`
- `outputs/inner_confusion_matrix.png`
- `outputs/clause_confusion_matrix.png`
- `outputs/evaluation_report.md`
- `outputs/nested_predictions.conll`

`evaluation_report.md` dosyasi her hedef sutun icin precision, recall,
f1-score, support, accuracy ve confusion matrix grafiklerini birlikte aciklar.

`nested_predictions.conll` dosyasi su formattadir:

```text
ID FORM GOLD_OUTER PRED_OUTER GOLD_INNER PRED_INNER GOLD_CLAUSE PRED_CLAUSE
```

## Tahmin

```bash
python src/predict.py
```

Komut calisinca kullanicidan Turkce bir cumle alinir, tokenlara ayrilir ve her
token icin su formatta nested chunking tahmini yazdirilir:

```text
ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE
```
