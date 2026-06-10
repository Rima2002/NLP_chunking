from pathlib import Path
import csv
import sys

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

try:
    from data_loader import load_conll, write_nested_predictions_conll
    from features import sent2features
except ImportError:
    from .data_loader import load_conll, write_nested_predictions_conll
    from .features import sent2features


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TEST_PATH = DATA_DIR / "test.conll"
MODEL_PATHS = {
    "outer": OUTPUT_DIR / "outer_model.pkl",
    "inner": OUTPUT_DIR / "inner_model.pkl",
    "clause": OUTPUT_DIR / "clause_model.pkl",
}
REPORT_PATHS = {
    "outer": OUTPUT_DIR / "outer_classification_report.txt",
    "inner": OUTPUT_DIR / "inner_classification_report.txt",
    "clause": OUTPUT_DIR / "clause_classification_report.txt",
}
MATRIX_PATHS = {
    "outer": OUTPUT_DIR / "outer_confusion_matrix.png",
    "inner": OUTPUT_DIR / "inner_confusion_matrix.png",
    "clause": OUTPUT_DIR / "clause_confusion_matrix.png",
}
COMBINED_MATRIX_PATH = OUTPUT_DIR / "all_confusion_matrices.png"
PREDICTIONS_PATH = OUTPUT_DIR / "nested_predictions.conll"
SUMMARY_REPORT_PATH = OUTPUT_DIR / "evaluation_report.md"
SUMMARY_TEXT_PATH = OUTPUT_DIR / "results_summary.txt"
METRICS_CSV_PATH = OUTPUT_DIR / "metrics_summary.csv"
ACCURACY_CSV_PATH = OUTPUT_DIR / "accuracy_summary.csv"
TARGET_TITLES = {
    "outer": "CHUNK-OUTER",
    "inner": "CHUNK-INNER",
    "clause": "CLAUSE",
}
TARGET_DESCRIPTIONS = {
    "outer": "Dis obekleri gosterir. NP, VP, ADVP ve O etiketleri kullanilir.",
    "inner": "Dis obek icindeki ic yapilari gosterir. Bu projede RELCL ve bos ic obek icin _ kullanilir.",
    "clause": "Cumlecikleri gosterir. RELCL, COMPCL ve cumlecik disi O etiketleri kullanilir.",
}


def sort_chunk_labels(labels: set[str] | list[str]) -> list[str]:
    def label_key(tag: str) -> tuple[int, str]:
        if tag == "_":
            return (98, tag)
        if tag == "O":
            return (99, tag)
        prefix, _, chunk_type = tag.partition("-")
        prefix_order = {"B": 0, "I": 1}.get(prefix, 2)
        return (prefix_order, chunk_type)

    return sorted(labels, key=label_key)


def flatten(sequences: list[list[str]]) -> list[str]:
    return [label for sequence in sequences for label in sequence]


def load_model(name: str):
    model_path = MODEL_PATHS[name]
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model bulunamadi: {model_path}. Once python src/train.py komutunu calistirin."
        )
    return joblib.load(model_path)


def save_confusion_matrix(
    matrix: list[list[int]],
    labels: list[str],
    title: str,
    matrix_path: Path,
) -> None:
    # Her hedef sutun icin ayri PNG confusion matrix grafigi uretilir.
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
    )
    plt.xlabel("Tahmin edilen etiket")
    plt.ylabel("Gercek etiket")
    plt.title(title)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(matrix_path, dpi=200)
    plt.close()


def save_combined_confusion_matrices(results: dict[str, dict]) -> None:
    # Uc confusion matrix tek gorselde de rapora eklenir.
    fig, axes = plt.subplots(1, 3, figsize=(24, 7))
    for axis, (name, result) in zip(axes, results.items()):
        sns.heatmap(
            result["matrix"],
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=result["labels"],
            yticklabels=result["labels"],
            ax=axis,
            cbar=name == "clause",
        )
        axis.set_title(f"{TARGET_TITLES[name]} Confusion Matrix")
        axis.set_xlabel("Tahmin edilen etiket")
        axis.set_ylabel("Gercek etiket")
        axis.tick_params(axis="x", rotation=45)
        axis.tick_params(axis="y", rotation=0)
    plt.tight_layout()
    plt.savefig(COMBINED_MATRIX_PATH, dpi=220)
    plt.close(fig)


def evaluate_target(
    name: str,
    model,
    X_test: list[list[dict]],
    y_test: list[list[str]],
) -> tuple[list[list[str]], float, list[str], dict, list[list[int]]]:
    predictions = model.predict(X_test)

    # Rapor ve confusion matrix token bazli duz listelerle hesaplanir.
    y_true = flatten(y_test)
    y_pred = flatten(predictions)
    labels = sort_chunk_labels(set(getattr(model, "classes_", [])) | set(y_true) | set(y_pred))

    accuracy = accuracy_score(y_true, y_pred)
    report_dict = classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )
    matrix = confusion_matrix(y_true, y_pred, labels=labels).tolist()

    write_target_report(name, accuracy, labels, report_dict, matrix)
    save_confusion_matrix(
        matrix,
        labels,
        f"{name.upper()} Confusion Matrix",
        MATRIX_PATHS[name],
    )

    print_target_result(name, accuracy, labels, report_dict)
    return predictions, accuracy, labels, report_dict, matrix


def format_metric(value: float) -> str:
    return f"{value:.4f}"


def build_metric_rows(labels: list[str], report_dict: dict) -> list[list[str]]:
    rows: list[list[str]] = []
    for label in labels:
        metrics = report_dict.get(label, {})
        rows.append(
            [
                label,
                format_metric(metrics.get("precision", 0.0)),
                format_metric(metrics.get("recall", 0.0)),
                format_metric(metrics.get("f1-score", 0.0)),
                str(int(metrics.get("support", 0))),
            ]
        )

    macro_avg = report_dict.get("macro avg", {})
    weighted_avg = report_dict.get("weighted avg", {})
    # Ortalama satirlari genel yorum icin saklanir.
    for label, metrics in (("Macro avg", macro_avg), ("Weighted avg", weighted_avg)):
        rows.append(
            [
                label,
                format_metric(metrics.get("precision", 0.0)),
                format_metric(metrics.get("recall", 0.0)),
                format_metric(metrics.get("f1-score", 0.0)),
                str(int(metrics.get("support", 0))),
            ]
        )
    return rows


def build_markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|---" + "|---:" * (len(headers) - 1) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def build_plain_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def format_row(row: list[str]) -> str:
        cells = [row[0].ljust(widths[0])]
        cells.extend(value.rjust(widths[index]) for index, value in enumerate(row[1:], start=1))
        return "  ".join(cells)

    separator = "  ".join("-" * width for width in widths)
    return [format_row(headers), separator, *[format_row(row) for row in rows]]


def build_metric_markdown_table(labels: list[str], report_dict: dict) -> list[str]:
    return build_markdown_table(
        ["Sinif", "Precision", "Recall", "F-measure", "Support"],
        build_metric_rows(labels, report_dict),
    )


def build_metric_plain_table(labels: list[str], report_dict: dict) -> list[str]:
    return build_plain_table(
        ["Sinif", "Precision", "Recall", "F-measure", "Support"],
        build_metric_rows(labels, report_dict),
    )


def write_target_report(
    name: str,
    accuracy: float,
    labels: list[str],
    report_dict: dict,
    matrix: list[list[int]],
) -> None:
    title = TARGET_TITLES[name]
    lines = [
        f"# {title} Classification Report",
        "",
        f"Accuracy: `{accuracy:.4f}`",
        "",
        "Kullanilan etiketler:",
        "",
        ", ".join(labels),
        "",
        "## Basari Metrikleri",
        "",
    ]
    lines.extend(build_metric_plain_table(labels, report_dict))
    lines.extend(
        [
            "",
            "## Confusion Matrix Sayisal Tablo",
            "",
        ]
    )
    lines.extend(build_confusion_matrix_plain_table(labels, matrix))
    lines.append("")
    REPORT_PATHS[name].write_text("\n".join(lines), encoding="utf-8")


def print_target_result(
    name: str,
    accuracy: float,
    labels: list[str],
    report_dict: dict,
) -> None:
    title = TARGET_TITLES[name]
    print(f"\n===== {title} =====")
    print(f"Genel model accuracy: {accuracy:.4f}")
    print("Proje sonuclari basari oranlari:")
    print("\n".join(build_metric_plain_table(labels, report_dict)))
    print(f"\nConfusion matrix grafik olarak kaydedildi: {MATRIX_PATHS[name]}")
    print(f"Rapor dosyasi: {REPORT_PATHS[name]}")


def build_accuracy_table(results: dict[str, dict]) -> list[str]:
    lines = [
        "| Hedef sutun | Accuracy | Rapor dosyasi | Confusion matrix grafigi |",
        "|---|---:|---|---|",
    ]
    for name, result in results.items():
        lines.append(
            "| "
            + TARGET_TITLES[name]
            + " | "
            + format_metric(result["accuracy"])
            + " | "
            + REPORT_PATHS[name].name
            + " | "
            + MATRIX_PATHS[name].name
            + " |"
        )
    return lines


def write_metrics_csv(results: dict[str, dict]) -> None:
    # Sinif bazli metrikler CSV dosyasina yazilir; accuracy ayri dosyada tutulur.
    with METRICS_CSV_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "target",
                "class",
                "precision",
                "recall",
                "f_measure",
                "support",
                "confusion_matrix_png",
            ]
        )
        for name, result in results.items():
            report_dict = result["report_dict"]
            for label in result["labels"]:
                metrics = report_dict.get(label, {})
                writer.writerow(
                    [
                        TARGET_TITLES[name],
                        label,
                        format_metric(metrics.get("precision", 0.0)),
                        format_metric(metrics.get("recall", 0.0)),
                        format_metric(metrics.get("f1-score", 0.0)),
                        int(metrics.get("support", 0)),
                        MATRIX_PATHS[name].name,
                    ]
                )


def write_accuracy_csv(results: dict[str, dict]) -> None:
    # Accuracy sinif bazli degil, model geneli icin hesaplanir.
    with ACCURACY_CSV_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["target", "accuracy"])
        for name, result in results.items():
            writer.writerow([TARGET_TITLES[name], format_metric(result["accuracy"])])


def write_text_summary(
    sentence_count: int,
    token_count: int,
    results: dict[str, dict],
) -> None:
    lines = [
        "NESTED CHUNKING PROJE SONUCLARI",
        "",
        f"Test cumlesi sayisi: {sentence_count}",
        f"Test token sayisi: {token_count}",
        "",
        "Genel basari oranlari:",
    ]
    summary_rows = [
        [TARGET_TITLES[name], format_metric(result["accuracy"]), MATRIX_PATHS[name].name]
        for name, result in results.items()
    ]
    lines.extend(build_plain_table(["Hedef", "Accuracy", "Confusion matrix PNG"], summary_rows))

    for name, result in results.items():
        lines.extend(
            [
                "",
                f"{TARGET_TITLES[name]} basari metrikleri",
                f"Confusion matrix grafigi: {MATRIX_PATHS[name].name}",
                "",
            ]
        )
        lines.extend(build_metric_plain_table(result["labels"], result["report_dict"]))

    lines.extend(
        [
            "",
            f"Birlesik confusion matrix grafigi: {COMBINED_MATRIX_PATH.name}",
            f"Markdown raporu: {SUMMARY_REPORT_PATH.name}",
            f"CSV metrik dosyasi: {METRICS_CSV_PATH.name}",
            f"CSV accuracy dosyasi: {ACCURACY_CSV_PATH.name}",
        ]
    )
    SUMMARY_TEXT_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_confusion_matrix_markdown_table(labels: list[str], matrix: list[list[int]]) -> list[str]:
    header = "| Gercek \\ Tahmin | " + " | ".join(labels) + " |"
    separator = "|---" + "|---:" * len(labels) + "|"
    lines = [header, separator]
    for label, row in zip(labels, matrix):
        lines.append("| " + label + " | " + " | ".join(str(value) for value in row) + " |")
    return lines


def build_confusion_matrix_plain_table(labels: list[str], matrix: list[list[int]]) -> list[str]:
    rows = [[label, *[str(value) for value in row]] for label, row in zip(labels, matrix)]
    return build_plain_table(["Gercek \\ Tahmin", *labels], rows)


def write_summary_report(
    sentence_count: int,
    token_count: int,
    results: dict[str, dict],
) -> None:
    lines = [
        "# Nested Chunking Degerlendirme Raporu",
        "",
        "Bu rapor `python src/evaluate.py` komutu ile otomatik uretilir.",
        "Projede istatistiksel makine ogrenmesi yontemi olarak Conditional Random Fields (CRF) kullanilmistir.",
        "",
        "## Veri ve Isaretleme Formati",
        "",
        "- Tum isaretlemeler CoNLL formatindadir.",
        "- Sutunlar: `ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE`.",
        "- `B` etiketi isaretlemenin baslangicini, `I` etiketi devamini gosterir.",
        "- `_` ic chunk bulunmadigini, `O` ilgili hedef icin disarida kalan tokeni gosterir.",
        f"- Test cumlesi sayisi: `{sentence_count}`.",
        f"- Test token sayisi: `{token_count}`.",
        "",
        "## Modelleme",
        "",
        "Ayni ozelliklerle uc ayri CRF modeli egitilmistir: `outer_model.pkl`, `inner_model.pkl` ve `clause_model.pkl`.",
        "Boylece dis obek, ic obek ve cumlecik sinirlari birbirinden bagimsiz raporlanabilir.",
        "",
        "## Sonuclar",
        "",
        "Precision, recall, f-measure ve accuracy degerleri `outputs` klasorune rapor olarak kaydedilir.",
        "Confusion matrix sonuclari PNG grafik dosyasi olarak uretilir.",
        "",
        "### Genel Basari Ozeti",
        "",
    ]
    lines.extend(build_accuracy_table(results))
    lines.extend(
        [
            "",
            "### Confusion Matrix Grafik Ozeti",
            "",
            "Asagidaki gorsel uc hedef sutunun karisiklik matrislerini grafik olarak birlikte gosterir.",
            "",
            f"![Tum confusion matrix grafikleri]({COMBINED_MATRIX_PATH.name})",
            "",
        ]
    )

    for name, result in results.items():
        title = TARGET_TITLES[name]
        matrix_file = MATRIX_PATHS[name].name
        lines.extend(
            [
                f"### {title}",
                "",
                TARGET_DESCRIPTIONS[name],
                "",
                f"- Accuracy: `{result['accuracy']:.4f}`",
                f"- Ayrintili metin raporu: `{REPORT_PATHS[name].name}`",
                f"- Confusion matrix grafigi: `{matrix_file}`",
                "",
                f"![{title} confusion matrix]({matrix_file})",
                "",
            ]
        )
        lines.extend(build_metric_markdown_table(result["labels"], result["report_dict"]))
        lines.append("")
        lines.append("Confusion matrix sayisal tablo:")
        lines.append("")
        lines.extend(build_confusion_matrix_markdown_table(result["labels"], result["matrix"]))
        lines.append("")

    lines.extend(
        [
            "## Tahmin Dosyasi",
            "",
            "`nested_predictions.conll` dosyasinda her token icin altin ve tahmin edilen etiketler birlikte verilir:",
            "",
            "```text",
            "ID FORM GOLD_OUTER PRED_OUTER GOLD_INNER PRED_INNER GOLD_CLAUSE PRED_CLAUSE",
            "```",
            "",
        ]
    )

    SUMMARY_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Test verisi yukleniyor: {TEST_PATH}")
    sentences, y_outer, y_inner, y_clause = load_conll(TEST_PATH)
    X_test = [sent2features(sentence) for sentence in sentences]

    # Egitimde kaydedilen uc model test verisi uzerinde ayri ayri denenir.
    print("Modeller yukleniyor...")
    outer_model = load_model("outer")
    inner_model = load_model("inner")
    clause_model = load_model("clause")

    pred_outer, outer_acc, outer_labels, outer_report, outer_matrix = evaluate_target(
        "outer", outer_model, X_test, y_outer
    )
    pred_inner, inner_acc, inner_labels, inner_report, inner_matrix = evaluate_target(
        "inner", inner_model, X_test, y_inner
    )
    pred_clause, clause_acc, clause_labels, clause_report, clause_matrix = evaluate_target(
        "clause", clause_model, X_test, y_clause
    )

    write_nested_predictions_conll(
        sentences,
        y_outer,
        pred_outer,
        y_inner,
        pred_inner,
        y_clause,
        pred_clause,
        PREDICTIONS_PATH,
    )
    results = {
        "outer": {
            "accuracy": outer_acc,
            "labels": outer_labels,
            "report_dict": outer_report,
            "matrix": outer_matrix,
        },
        "inner": {
            "accuracy": inner_acc,
            "labels": inner_labels,
            "report_dict": inner_report,
            "matrix": inner_matrix,
        },
        "clause": {
            "accuracy": clause_acc,
            "labels": clause_labels,
            "report_dict": clause_report,
            "matrix": clause_matrix,
        },
    }
    save_combined_confusion_matrices(results)
    write_metrics_csv(results)
    write_accuracy_csv(results)
    write_text_summary(
        sentence_count=len(sentences),
        token_count=sum(len(sentence) for sentence in sentences),
        results=results,
    )
    write_summary_report(
        sentence_count=len(sentences),
        token_count=sum(len(sentence) for sentence in sentences),
        results=results,
    )

    print("\n===== OUTPUT DOSYALARI =====")
    print("Basari oranlari terminalde yukarida gosterildi ve outputs klasorune kaydedildi.")
    print(f"Metin sonuc ozeti: {SUMMARY_TEXT_PATH}")
    print(f"CSV metrik dosyasi: {METRICS_CSV_PATH}")
    print(f"CSV accuracy dosyasi: {ACCURACY_CSV_PATH}")
    print(f"Birlesik degerlendirme raporu: {SUMMARY_REPORT_PATH}")
    print("\nConfusion matrix grafik dosyalari:")
    print(f"OUTER grafik: {MATRIX_PATHS['outer']}")
    print(f"INNER grafik: {MATRIX_PATHS['inner']}")
    print(f"CLAUSE grafik: {MATRIX_PATHS['clause']}")
    print(f"Birlesik grafik: {COMBINED_MATRIX_PATH}")
    print("\nGenel accuracy degerleri:")
    print(f"OUTER: {outer_acc:.4f}")
    print(f"INNER: {inner_acc:.4f}")
    print(f"CLAUSE: {clause_acc:.4f}")
    print(f"Tahmin dosyasi: {PREDICTIONS_PATH}")


if __name__ == "__main__":
    main()
