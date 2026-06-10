from pathlib import Path
from typing import Iterable


Sentence = list[str]
LabelSequence = list[str]


def load_conll(
    filepath: str | Path,
) -> tuple[list[Sentence], list[LabelSequence], list[LabelSequence], list[LabelSequence]]:
    """Load 5-column nested chunking CoNLL data.

    Expected columns are:
    ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"CoNLL veri dosyasi bulunamadi: {path}. "
            "Lutfen data/train.conll ve data/test.conll dosyalarini kontrol edin."
        )

    sentences: list[Sentence] = []
    y_outer: list[LabelSequence] = []
    y_inner: list[LabelSequence] = []
    y_clause: list[LabelSequence] = []

    sentence_tokens: Sentence = []
    outer_tags: LabelSequence = []
    inner_tags: LabelSequence = []
    clause_tags: LabelSequence = []

    with path.open(encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()

            # Bos satir cumlenin bittigini gosterir.
            if not line:
                if sentence_tokens:
                    sentences.append(sentence_tokens)
                    y_outer.append(outer_tags)
                    y_inner.append(inner_tags)
                    y_clause.append(clause_tags)
                    sentence_tokens = []
                    outer_tags = []
                    inner_tags = []
                    clause_tags = []
                continue

            if line.startswith("#"):
                continue

            parts = line.split()
            # Her token satiri tam olarak 5 sutunlu CoNLL formatinda olmali.
            if len(parts) != 5:
                raise ValueError(
                    f"Yanlis sutun sayisi: {path}:{line_number}. "
                    "Beklenen format: ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE"
                )

            token_id, form, chunk_outer, chunk_inner, clause = parts
            if not token_id.isdigit():
                raise ValueError(f"Gecersiz ID: {path}:{line_number}. ID sayisal olmali.")

            # Model sadece FORM alanini token olarak kullanir; uc etiket ayri tutulur.
            sentence_tokens.append(form)
            outer_tags.append(chunk_outer)
            inner_tags.append(chunk_inner)
            clause_tags.append(clause)

    if sentence_tokens:
        sentences.append(sentence_tokens)
        y_outer.append(outer_tags)
        y_inner.append(inner_tags)
        y_clause.append(clause_tags)

    if not sentences:
        raise ValueError(f"CoNLL dosyasi bos veya cumle icermiyor: {path}")

    return sentences, y_outer, y_inner, y_clause


def write_nested_predictions_conll(
    sentences: Iterable[Sentence],
    gold_outer: Iterable[LabelSequence],
    pred_outer: Iterable[LabelSequence],
    gold_inner: Iterable[LabelSequence],
    pred_inner: Iterable[LabelSequence],
    gold_clause: Iterable[LabelSequence],
    pred_clause: Iterable[LabelSequence],
    filepath: str | Path,
) -> None:
    """Write nested chunking predictions in the requested CoNLL-like format."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as output_file:
        output_file.write(
            "# columns = ID FORM GOLD_OUTER PRED_OUTER "
            "GOLD_INNER PRED_INNER GOLD_CLAUSE PRED_CLAUSE\n"
        )
        rows = zip(sentences, gold_outer, pred_outer, gold_inner, pred_inner, gold_clause, pred_clause)
        for sentence, go, po, gi, pi, gc, pc in rows:
            lengths = {len(sentence), len(go), len(po), len(gi), len(pi), len(gc), len(pc)}
            # Tahmin ve gercek etiket sayilari token sayisiyla ayni olmali.
            if len(lengths) != 1:
                raise ValueError("Tahmin ciktisi yazilirken token/etiket uzunluklari eslesmedi.")

            for index, values in enumerate(zip(sentence, go, po, gi, pi, gc, pc), start=1):
                token, gold_o, pred_o, gold_i, pred_i, gold_c, pred_c = values
                output_file.write(
                    f"{index} {token} {gold_o} {pred_o} "
                    f"{gold_i} {pred_i} {gold_c} {pred_c}\n"
                )
            output_file.write("\n")
