# Turkce Nested Chunking Projesi

Bu proje, Turkce cumlelerde isim obekleri (NP), eylem obekleri (VP), zarf
obekleri (ADVP), ic ice gecen ilgi cumlecikleri (RELCL) ve tumlec
cumleciklerini (COMPCL) etiketlemek icin hazirlanmistir.

Projede istatistiksel makine ogrenmesi yontemi olarak Conditional Random Fields
(CRF) kullanilir. `CHUNK-OUTER`, `CHUNK-INNER` ve `CLAUSE` sutunlari icin uc ayri
CRF modeli egitilir.

## Proje Yapisi

```text
chunking_project/
|-- data/
|   |-- train.conll
|   `-- test.conll
|-- outputs/
|   |-- outer_model.pkl
|   |-- inner_model.pkl
|   |-- clause_model.pkl
|   |-- results_summary.txt
|   |-- metrics_summary.csv
|   |-- accuracy_summary.csv
|   |-- evaluation_report.md
|   |-- outer_confusion_matrix.png
|   |-- inner_confusion_matrix.png
|   |-- clause_confusion_matrix.png
|   `-- all_confusion_matrices.png
|-- src/
|   |-- data_loader.py
|   |-- features.py
|   |-- train.py
|   |-- evaluate.py
|   `-- predict.py
|-- requirements.txt
`-- README.md
```

## Veri Formati

Veriler CoNLL formatindadir. Her satirda 5 sutun bulunur:

```text
ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE
```

Cumleler bos satirla ayrilir.

Ornek:

```text
1 Dun B-ADVP _ O
2 aksam I-ADVP _ O
3 toplantidan B-NP B-RELCL B-RELCL
4 erken I-NP I-RELCL I-RELCL
5 cikan I-NP I-RELCL I-RELCL
6 ogrencinin I-NP _ O
```

## Etiketler

- `B`: Isaretlemenin baslangicini gosterir.
- `I`: Isaretlemenin devamini gosterir.
- `_`: Ic chunk olmadigini gosterir.
- `O`: Ilgili sutunda chunk veya cumlecik disinda kalan tokeni gosterir.

Sutunlar:

- `CHUNK-OUTER`: Dis obek etiketi. `NP`, `VP`, `ADVP`, `O` kullanilir.
- `CHUNK-INNER`: Ic obek etiketi. Bu projede ozellikle `RELCL` kullanilir.
- `CLAUSE`: Cumlecik etiketi. `RELCL`, `COMPCL`, `O` kullanilir.

## Kurulum

VS Code terminalinde proje klasorune girin:

```powershell
cd "...\chunking_project"
```

Gerekli kutuphaneleri kurun:

```powershell
pip install -r requirements.txt
```

## Egitim

```powershell
python src\train.py
```

Bu komut `data/train.conll` dosyasini okur ve uc ayri model olusturur:

- `outputs/outer_model.pkl`
- `outputs/inner_model.pkl`
- `outputs/clause_model.pkl`

## Degerlendirme

```powershell
python src\evaluate.py
```

Bu komut `data/test.conll` dosyasinda modelleri test eder. Terminalde
precision, recall, f-measure ve genel model accuracy degerleri gosterilir.

Uretilen onemli output dosyalari:

- `outputs/results_summary.txt`
- `outputs/metrics_summary.csv`
- `outputs/accuracy_summary.csv`
- `outputs/evaluation_report.md`
- `outputs/nested_predictions.conll`

Confusion matrix grafikleri:

- `outputs/outer_confusion_matrix.png`
- `outputs/inner_confusion_matrix.png`
- `outputs/clause_confusion_matrix.png`
- `outputs/all_confusion_matrices.png`

## Tahmin

```powershell
python src\predict.py
```

Komut calistiktan sonra Turkce bir cumle girilir. Cikti su formatta verilir:

```text
ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE
```

Ornek cumle:

```text
Dun aksam toplantidan erken cikan ogrencinin makaleyi okudugunu fark ettim.
```

## Dosyalarin Gorevi

- `src/data_loader.py`: 5 sutunlu CoNLL verisini okur.
- `src/features.py`: CRF modeli icin kelime ozelliklerini cikarir.
- `src/train.py`: Uc ayri CRF modelini egitir.
- `src/evaluate.py`: Modelleri test eder, metrikleri ve confusion matrix grafiklerini uretir.
- `src/predict.py`: Kullanici cumlesi icin nested chunking tahmini yapar.

## Not

Veri seti egitim amaclidir ve kucuk olceklidir. Bu nedenle bazi etiketlerde
basari dusuk cikabilir. Kod, veri formati ve raporlama akisi proje isterlerini
karsilayacak sekilde hazirlanmistir.
