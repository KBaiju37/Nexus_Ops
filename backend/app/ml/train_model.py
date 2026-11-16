import os
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.ml.training_data import FALLBACK_RULES, LOG_TRAINING_DATA

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "log_classifier.joblib"


def build_model_pipeline():
    texts = []
    labels = []
    for category, examples in LOG_TRAINING_DATA.items():
        for example in examples:
            texts.append(example)
            labels.append(category)
    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )
    model.fit(texts, labels)
    return model


def train_and_save_model(path: str | os.PathLike = MODEL_PATH):
    pipeline = build_model_pipeline()
    joblib.dump(pipeline, path)
    return pipeline


def load_model(path: str | os.PathLike = MODEL_PATH):
    if not os.path.exists(path):
        return train_and_save_model(path)
    return joblib.load(path)


def fallback_classification(logs: str):
    lowered = logs.lower()
    for keyword, config in FALLBACK_RULES.items():
        if keyword in lowered:
            return config
    if "database" in lowered or "postgres" in lowered or "sql" in lowered:
        return FALLBACK_RULES["database connection failure"]
    if "memory" in lowered or "oom" in lowered or "heap" in lowered:
        return FALLBACK_RULES["memory/resource problem"]
    if "timeout" in lowered or "network" in lowered or "socket" in lowered:
        return FALLBACK_RULES["network timeout"]
    if "exception" in lowered or "traceback" in lowered or "error" in lowered:
        return FALLBACK_RULES["application exception"]
    if "auth" in lowered or "jwt" in lowered or "token" in lowered or "401" in lowered or "403" in lowered:
        return FALLBACK_RULES["authentication failure"]
    if "dependency" in lowered or "build" in lowered or "module" in lowered or "install" in lowered:
        return FALLBACK_RULES["dependency/build failure"]
    return FALLBACK_RULES["application exception"]
