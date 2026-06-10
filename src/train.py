from pathlib import Path
import sys

import joblib
from sklearn_crfsuite import CRF

try:
    from data_loader import load_conll
    from features import sent2features, sent2labels
except ImportError:
    from .data_loader import load_conll
    from .features import sent2features, sent2labels


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TRAIN_PATH = DATA_DIR / "train.conll"
MODEL_PATHS = {
    "OUTER": OUTPUT_DIR / "outer_model.pkl",
    "INNER": OUTPUT_DIR / "inner_model.pkl",
    "CLAUSE": OUTPUT_DIR / "clause_model.pkl",
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


def collect_labels(label_sequences: list[list[str]]) -> list[str]:
    return sort_chunk_labels({label for labels in label_sequences for label in labels})


def build_crf() -> CRF:
    # Ayni CRF ayarlari uc hedef sutun icin de kullanilir.
    return CRF(
        algorithm="lbfgs",
        c1=0.1,
        c2=0.1,
        max_iterations=200,
        all_possible_transitions=True,
    )


def train_single_model(
    name: str,
    X_train: list[list[dict]],
    y_train_raw: list[list[str]],
) -> CRF:
    dataset_labels = collect_labels(y_train_raw)
    print(f"\n{name} modeli egitiliyor...")
    print(f"{name} egitim etiketleri: {', '.join(dataset_labels)}")

    model = build_crf()
    y_train = [sent2labels(labels) for labels in y_train_raw]
    model.fit(X_train, y_train)
    return model


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Egitim verisi yukleniyor: {TRAIN_PATH}")
    sentences, y_outer, y_inner, y_clause = load_conll(TRAIN_PATH)
    X_train = [sent2features(sentence) for sentence in sentences]

    # Nested chunking icin her hedef sutun ayri model olarak egitilir.
    targets = {
        "OUTER": y_outer,
        "INNER": y_inner,
        "CLAUSE": y_clause,
    }

    for name, labels in targets.items():
        model = train_single_model(name, X_train, labels)
        joblib.dump(model, MODEL_PATHS[name])
        used_labels = sort_chunk_labels(list(model.classes_))
        print(f"{name} modeli kaydedildi: {MODEL_PATHS[name]}")
        print(f"{name} modelinde kullanilan etiketler: {', '.join(used_labels)}")


if __name__ == "__main__":
    main()
