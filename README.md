# Türkçe Nested Chunking Projesi

Bu proje, Türkçe cümlelerde isim öbekleri (NP), eylem öbekleri (VP), zarf
öbekleri (ADVP), iç içe geçen ilgi cümlecikleri (RELCL) ve tümleç
cümleciklerini (COMPCL) etiketlemek için hazırlanmıştır.

Projede istatistiksel makine öğrenmesi yöntemi olarak Conditional Random Fields
(CRF) kullanılır. `CHUNK-OUTER`, `CHUNK-INNER` ve `CLAUSE` sütunları için üç ayrı
CRF modeli eğitilir.

## Proje Yapısı

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

## Veri Formatı

Veriler CoNLL formatındadır. Her satırda 5 sütun bulunur:

```text
ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE
```

Cümleler boş satırla ayrılır.

Örnek:

```text
1 Dün B-ADVP _ O
2 akşam I-ADVP _ O
3 toplantıdan B-NP B-RELCL B-RELCL
4 erken I-NP I-RELCL I-RELCL
5 çıkan I-NP I-RELCL I-RELCL
6 öğrencinin I-NP _ O
```

## Etiketler

- `B`: İşaretlemenin başlangıcını gösterir.
- `I`: İşaretlemenin devamını gösterir.
- `_`: İç chunk olmadığını gösterir.
- `O`: İlgili sütunda chunk veya cümlecik dışında kalan tokeni gösterir.

Sütunlar:

- `CHUNK-OUTER`: Dış öbek etiketi. `NP`, `VP`, `ADVP`, `O` kullanılır.
- `CHUNK-INNER`: İç öbek etiketi. Bu projede özellikle `RELCL` kullanılır.
- `CLAUSE`: Cümlecik etiketi. `RELCL`, `COMPCL`, `O` kullanılır.

## Kurulum

VS Code terminalinde proje klasörüne girin:

```powershell
cd "...\chunking_project"
```

Gerekli kütüphaneleri kurun:

```powershell
pip install -r requirements.txt
```

## Eğitim

```powershell
python src\train.py
```

Bu komut `data/train.conll` dosyasını okur ve üç ayrı model oluşturur:

- `outputs/outer_model.pkl`
- `outputs/inner_model.pkl`
- `outputs/clause_model.pkl`

## Değerlendirme

```powershell
python src\evaluate.py
```

Bu komut `data/test.conll` dosyasında modelleri test eder. Terminalde
precision, recall, f-measure ve genel model accuracy değerleri gösterilir.

Üretilen önemli output dosyaları:

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

Komut çalıştıktan sonra Türkçe bir cümle girilir. Çıktı şu formatta verilir:

```text
ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE
```

Örnek cümle:

```text
Dün akşam toplantıdan erken çıkan öğrencinin makaleyi okuduğunu fark ettim.
```

## Dosyaların Görevi

- `src/data_loader.py`: 5 sütunlu CoNLL verisini okur.
- `src/features.py`: CRF modeli için kelime özelliklerini çıkarır.
- `src/train.py`: Üç ayrı CRF modelini eğitir.
- `src/evaluate.py`: Modelleri test eder, metrikleri ve confusion matrix grafiklerini üretir.
- `src/predict.py`: Kullanıcı cümlesi için nested chunking tahmini yapar.

## Not

Veri seti eğitim amaçlıdır ve küçük ölçeklidir. Bu nedenle bazı etiketlerde
başarı düşük çıkabilir. Kod, veri formatı ve raporlama akışı proje isterlerini
karşılayacak şekilde hazırlanmıştır.
