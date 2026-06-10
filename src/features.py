from string import punctuation
from typing import Any


FeatureDict = dict[str, Any]
TURKISH_PUNCTUATION = punctuation + "“”‘’…"


def _suffix(token: str, size: int) -> str:
    return token[-size:] if len(token) >= size else token


def _prefix(token: str, size: int) -> str:
    return token[:size]


def _basic_token_features(prefix: str, token: str) -> FeatureDict:
    # CRF modeli icin kelimenin yuzeysel bicim ozellikleri.
    return {
        f"{prefix}.word": token,
        f"{prefix}.lower": token.lower(),
        f"{prefix}.prefix2": _prefix(token, 2),
        f"{prefix}.prefix3": _prefix(token, 3),
        f"{prefix}.suffix2": _suffix(token, 2),
        f"{prefix}.suffix3": _suffix(token, 3),
        f"{prefix}.length": len(token),
        f"{prefix}.istitle": token.istitle(),
        f"{prefix}.isupper": token.isupper(),
        f"{prefix}.isdigit": token.isdigit(),
        f"{prefix}.ispunct": bool(token) and all(char in TURKISH_PUNCTUATION for char in token),
    }


def word2features(sentence: list[str], index: int) -> FeatureDict:
    """Extract lexical and contextual features for one token."""
    token = sentence[index]
    features: FeatureDict = {"bias": 1.0}

    # Kelimenin kendisi ve cumledeki konumu modele verilir.
    features.update(_basic_token_features("token", token))
    features["is_sentence_start"] = index == 0
    features["is_sentence_end"] = index == len(sentence) - 1

    # Onceki ve sonraki kelime bilgisi chunk sinirlarini yakalamaya yardim eder.
    if index > 0:
        features.update(_basic_token_features("prev", sentence[index - 1]))
    else:
        features["BOS"] = True

    if index < len(sentence) - 1:
        features.update(_basic_token_features("next", sentence[index + 1]))
    else:
        features["EOS"] = True

    return features


def sent2features(sentence: list[str]) -> list[FeatureDict]:
    return [word2features(sentence, index) for index in range(len(sentence))]


def sent2labels(tags: list[str]) -> list[str]:
    return list(tags)
