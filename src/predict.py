from pathlib import Path
import re
import sys

import joblib

try:
    from features import sent2features
except ImportError:
    from .features import sent2features


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MODEL_PATHS = {
    "outer": OUTPUT_DIR / "outer_model.pkl",
    "inner": OUTPUT_DIR / "inner_model.pkl",
    "clause": OUTPUT_DIR / "clause_model.pkl",
}


def tokenize(text: str) -> list[str]:
    """Tokenize Unicode words and keep punctuation as separate tokens."""
    # Kelimeleri ve noktalama isaretlerini ayri tokenlara boler.
    pattern = r"[^\W_]+|[^\w\s]"
    return re.findall(pattern, text, flags=re.UNICODE)


def load_model(name: str):
    model_path = MODEL_PATHS[name]
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model bulunamadi: {model_path}. Once python src/train.py komutunu calistirin."
        )
    return joblib.load(model_path)


def format_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def format_row(row: list[str]) -> str:
        return "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))

    separator = "  ".join("-" * width for width in widths)
    return [format_row(headers), separator, *[format_row(row) for row in rows]]


def main() -> None:
    try:
        sentence = input("Turkce bir cumle girin: ").strip()
    except EOFError:
        print("Cumle girisi alinmadi.")
        return

    if not sentence:
        print("Lutfen bos olmayan bir cumle girin.")
        return

    tokens = tokenize(sentence)
    if not tokens:
        print("Cumle tokenlara ayrilamadi.")
        return

    features = [sent2features(tokens)]
    outer_model = load_model("outer")
    inner_model = load_model("inner")
    clause_model = load_model("clause")

    pred_outer = outer_model.predict(features)[0]
    pred_inner = inner_model.predict(features)[0]
    pred_clause = clause_model.predict(features)[0]

    # Tahminler terminalde hizali CoNLL benzeri tablo olarak gosterilir.
    headers = ["ID", "FORM", "CHUNK-OUTER", "CHUNK-INNER", "CLAUSE"]
    rows = []
    for index, values in enumerate(zip(tokens, pred_outer, pred_inner, pred_clause), start=1):
        token, outer, inner, clause = values
        rows.append([str(index), token, outer, inner, clause])

    print()
    print("\n".join(format_table(headers, rows)))


if __name__ == "__main__":
    main()
