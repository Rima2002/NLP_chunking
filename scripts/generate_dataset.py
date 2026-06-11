from __future__ import annotations

from pathlib import Path
import random
import sys


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
TRAIN_PATH = DATA_DIR / "train.conll"
TEST_PATH = DATA_DIR / "test.conll"

HEADER = "# columns = ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE"
RANDOM_SEED = 467
TRAIN_SIZE = 320
TEST_SIZE = 80
TOTAL_SIZE = TRAIN_SIZE + TEST_SIZE

Token = tuple[str, str, str, str]
Sentence = list[Token]


subjects = [
    "Ali",
    "Ayşe",
    "Öğrenci",
    "Öğretmen",
    "Doktor",
    "Mühendis",
    "Araştırmacı",
    "Müdür",
    "Hemşire",
    "Çocuk",
    "Ekip",
    "Komisyon",
    "Yazar",
    "Uzman",
    "Sekreter",
    "Danışman",
    "Programcı",
    "Gazeteci",
    "Avukat",
    "Çevirmen",
]

objects = [
    "kitabı",
    "raporu",
    "makaleyi",
    "projeyi",
    "dosyayı",
    "notları",
    "sonuçları",
    "verileri",
    "planı",
    "öneriyi",
    "metni",
    "tabloyu",
    "sunumu",
    "taslağı",
    "başvuruyu",
    "belgeyi",
]

locations = [
    "okulda",
    "kütüphanede",
    "laboratuvarda",
    "sınıfta",
    "hastanede",
    "ofiste",
    "toplantıda",
    "bahçede",
    "salonda",
    "arşivde",
    "atölyede",
    "merkezde",
]

destinations = [
    "okula",
    "kütüphaneye",
    "laboratuvara",
    "sınıfa",
    "hastaneye",
    "ofise",
    "toplantıya",
    "bahçeye",
    "salona",
    "arşive",
]

adverbs = [
    "dikkatlice",
    "hızlıca",
    "sessizce",
    "açıkça",
    "titizlikle",
    "yeniden",
    "hemen",
    "bugün",
    "dün",
    "yarın",
    "sakince",
    "ayrıntılı",
]

time_phrases = [
    ["sabah", "erken"],
    ["dün", "akşam"],
    ["bugün", "öğleden", "sonra"],
    ["yarın", "sabah"],
    ["geçen", "hafta"],
    ["bu", "sabah"],
    ["akşam", "geç"],
]

verbs = [
    "okudu",
    "inceledi",
    "tamamladı",
    "anlattı",
    "gönderdi",
    "hazırladı",
    "sundu",
    "tartıştı",
    "değerlendirdi",
    "duyurdu",
    "düzenledi",
    "yazdı",
    "karşılaştırdı",
    "paylaştı",
]

movement_verbs = [
    "gitti",
    "geldi",
    "çıktı",
    "yetişti",
    "döndü",
    "uğradı",
    "ilerledi",
    "yaklaştı",
]

compound_verbs = [
    ("fark", "etti"),
    ("teslim", "etti"),
    ("kontrol", "etti"),
    ("not", "aldı"),
    ("kayıt", "yaptı"),
    ("yardım", "etti"),
]

rel_subjects = [
    "öğretmenin",
    "hocanın",
    "araştırmacının",
    "müdürün",
    "doktorun",
    "ekibin",
    "yazarın",
    "öğrencinin",
    "komisyonun",
    "danışmanın",
    "programcının",
    "gazetecinin",
]

rel_verbs = [
    "önerdiği",
    "anlattığı",
    "hazırladığı",
    "bulduğu",
    "yazdığı",
    "incelediği",
    "sunduğu",
    "düzenlediği",
    "seçtiği",
    "geliştirdiği",
    "değerlendirdiği",
    "çevirdiği",
]

rel_heads = [
    "makaleyi",
    "konuyu",
    "raporu",
    "projeyi",
    "dosyayı",
    "sonuçları",
    "verileri",
    "planı",
    "öneriyi",
    "metni",
    "sunumu",
    "taslağı",
]

comp_subjects = [
    "projenin",
    "raporun",
    "deneyin",
    "toplantının",
    "başvurunun",
    "sonucun",
    "sistemin",
    "planın",
    "dosyanın",
    "sunumun",
    "metnin",
    "modelin",
]

comp_single_verbs = [
    "tamamlandığını",
    "geciktiğini",
    "başladığını",
    "bittiğini",
    "onaylandığını",
    "değiştiğini",
    "iyileştiğini",
    "hazırlandığını",
]

comp_adjectives = [
    "başarılı",
    "önemli",
    "gerekli",
    "uygun",
    "yeterli",
    "eksik",
    "doğru",
    "anlaşılır",
]

main_cognition_verbs = [
    "gördük",
    "düşündüm",
    "söyledi",
    "duyduk",
    "fark",
    "belirtti",
    "anladık",
    "açıkladı",
]


def np(word: str, prefix: str = "B") -> Token:
    return (word, f"{prefix}-NP", "_", "O")


def advp(words: list[str]) -> Sentence:
    return [
        (word, "B-ADVP" if index == 0 else "I-ADVP", "_", "O")
        for index, word in enumerate(words)
    ]


def vp(word: str, prefix: str = "B") -> Token:
    return (word, f"{prefix}-VP", "_", "O")


def punct(mark: str = ".") -> Token:
    return (mark, "O", "_", "O")


def rel_np(rel_subject: str, rel_verb: str, head: str) -> Sentence:
    return [
        (rel_subject, "B-NP", "B-RELCL", "B-RELCL"),
        (rel_verb, "I-NP", "I-RELCL", "I-RELCL"),
        (head, "I-NP", "_", "O"),
    ]


def comp_clause_single(subject: str, verb: str) -> Sentence:
    return [
        (subject, "B-NP", "_", "B-COMPCL"),
        (verb, "B-VP", "_", "I-COMPCL"),
    ]


def comp_clause_adjective(subject: str, adjective: str) -> Sentence:
    return [
        (subject, "B-NP", "_", "B-COMPCL"),
        (adjective, "B-NP", "_", "I-COMPCL"),
        ("olduğunu", "B-VP", "_", "I-COMPCL"),
    ]


def simple_transitive(rng: random.Random) -> Sentence:
    sentence: Sentence = [np(rng.choice(subjects)), np(rng.choice(objects))]
    if rng.random() < 0.55:
        sentence += advp([rng.choice(adverbs)])
    if rng.random() < 0.35:
        sentence = advp(rng.choice(time_phrases)) + sentence
    sentence.append(vp(rng.choice(verbs)))
    sentence.append(punct())
    return sentence


def simple_location(rng: random.Random) -> Sentence:
    sentence: Sentence = []
    if rng.random() < 0.4:
        sentence += advp(rng.choice(time_phrases))
    sentence += [
        np(rng.choice(subjects)),
        np(rng.choice(destinations if rng.random() < 0.5 else locations)),
    ]
    if rng.random() < 0.45:
        sentence += advp([rng.choice(adverbs)])
    sentence += [vp(rng.choice(movement_verbs)), punct()]
    return sentence


def relative_object_sentence(rng: random.Random) -> Sentence:
    sentence: Sentence = []
    if rng.random() < 0.35:
        sentence += advp(rng.choice(time_phrases))
    sentence += rel_np(rng.choice(rel_subjects), rng.choice(rel_verbs), rng.choice(rel_heads))
    sentence += [np(rng.choice(subjects))]
    if rng.random() < 0.65:
        sentence += advp([rng.choice(adverbs)])
    sentence += [vp(rng.choice(verbs)), punct()]
    return sentence


def relative_subject_sentence(rng: random.Random) -> Sentence:
    acted_object = rng.choice(objects)
    action_adverb = rng.choice(adverbs)
    head = rng.choice(["öğrenci", "çocuk", "araştırmacı", "uzman", "mühendis", "yazar"])
    sentence: Sentence = [
        (acted_object, "B-NP", "B-RELCL", "B-RELCL"),
        (action_adverb, "I-NP", "I-RELCL", "I-RELCL"),
        (rng.choice(["okuyan", "inceleyen", "hazırlayan", "düzenleyen", "anlatan"]), "I-NP", "I-RELCL", "I-RELCL"),
        (head, "I-NP", "_", "O"),
        np(rng.choice(locations)),
        vp(rng.choice(movement_verbs + verbs)),
        punct(),
    ]
    return sentence


def complement_sentence(rng: random.Random) -> Sentence:
    sentence: Sentence = [np(rng.choice(subjects))]
    if rng.random() < 0.5:
        sentence += comp_clause_single(rng.choice(comp_subjects), rng.choice(comp_single_verbs))
    else:
        sentence += comp_clause_adjective(rng.choice(comp_subjects), rng.choice(comp_adjectives))
    if rng.random() < 0.35:
        sentence += advp([rng.choice(adverbs)])

    main_verb = rng.choice(main_cognition_verbs)
    if main_verb == "fark":
        sentence += [vp("fark"), vp("etti", "I")]
    else:
        sentence.append(vp(main_verb))
    sentence.append(punct())
    return sentence


def compound_verb_sentence(rng: random.Random) -> Sentence:
    first, second = rng.choice(compound_verbs)
    sentence: Sentence = [
        np(rng.choice(subjects)),
        np(rng.choice(objects)),
    ]
    if rng.random() < 0.6:
        sentence += advp([rng.choice(adverbs)])
    sentence += [vp(first), vp(second, "I"), punct()]
    return sentence


def nested_mixed_sentence(rng: random.Random) -> Sentence:
    first, second = rng.choice(compound_verbs)
    sentence: Sentence = []
    sentence += advp(rng.choice(time_phrases))
    sentence += rel_np(rng.choice(rel_subjects), rng.choice(rel_verbs), rng.choice(rel_heads))
    sentence += comp_clause_single(rng.choice(comp_subjects), rng.choice(comp_single_verbs))
    sentence += [vp(first), vp(second, "I"), punct()]
    return sentence


generators = [
    simple_transitive,
    simple_location,
    relative_object_sentence,
    relative_subject_sentence,
    complement_sentence,
    compound_verb_sentence,
    nested_mixed_sentence,
]


def sentence_key(sentence: Sentence) -> str:
    return " ".join(token[0] for token in sentence)


def validate(sentence: Sentence) -> None:
    for token in sentence:
        if len(token) != 4:
            raise ValueError(f"Token must have 4 fields before ID is added: {token}")
        word, outer, inner, clause = token
        if not word or not outer or not inner or not clause:
            raise ValueError(f"Empty field in token: {token}")


def build_dataset() -> list[Sentence]:
    rng = random.Random(RANDOM_SEED)
    dataset: list[Sentence] = []
    seen: set[str] = set()

    attempts = 0
    while len(dataset) < TOTAL_SIZE:
        generator = generators[len(dataset) % len(generators)]
        sentence = generator(rng)
        key = sentence_key(sentence)
        attempts += 1

        if key in seen:
            if attempts > TOTAL_SIZE * 50:
                raise RuntimeError("Could not create enough unique sentences.")
            continue

        validate(sentence)
        seen.add(key)
        dataset.append(sentence)

    rng.shuffle(dataset)
    return dataset


def write_conll(path: Path, sentences: list[Sentence]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(f"{HEADER}\n")
        for sentence in sentences:
            for index, (word, outer, inner, clause) in enumerate(sentence, start=1):
                file.write(f"{index} {word} {outer} {inner} {clause}\n")
            file.write("\n")


def main() -> None:
    dataset = build_dataset()
    train_sentences = dataset[:TRAIN_SIZE]
    test_sentences = dataset[TRAIN_SIZE:]

    write_conll(TRAIN_PATH, train_sentences)
    write_conll(TEST_PATH, test_sentences)

    print(f"Train sentences: {len(train_sentences)} -> {TRAIN_PATH}")
    print(f"Test sentences: {len(test_sentences)} -> {TEST_PATH}")
    print(f"Total sentences: {len(dataset)}")


if __name__ == "__main__":
    main()
