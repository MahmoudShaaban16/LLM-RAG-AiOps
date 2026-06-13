"""
Solution: Exercise 1 - Implement cosine similarity from scratch
"""

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

TEST_VECTORS = [
    ("identical vectors", np.array([1.0, 0.0]), np.array([1.0, 0.0]), 1.0),
    ("orthogonal vectors", np.array([1.0, 0.0]), np.array([0.0, 1.0]), 0.0),
    ("opposite vectors", np.array([1.0, 0.0]), np.array([-1.0, 0.0]), -1.0),
    ("scaled but same direction", np.array([1.0, 2.0]), np.array([2.0, 4.0]), 1.0),
]

SAMPLE_SENTENCES = [
    "The cat sat on the mat.",
    "A kitten rested on a rug.",
    "Quarterly revenue grew by 12% year over year.",
]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """cosine_similarity(a, b) = (a . b) / (||a|| * ||b||)"""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return float(dot / (norm_a * norm_b))


def main() -> None:
    print("=== Test vectors ===")
    for name, a, b, expected in TEST_VECTORS:
        result = cosine_similarity(a, b)
        print(f"{name}: got={result:.3f} expected={expected:.3f}")

    print("\n=== Sample sentences ===")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(SAMPLE_SENTENCES)

    for i in range(len(SAMPLE_SENTENCES)):
        for j in range(i + 1, len(SAMPLE_SENTENCES)):
            similarity = cosine_similarity(embeddings[i], embeddings[j])
            print(f"[{i}] vs [{j}]: {similarity:.3f}")
            print(f"    [{i}] {SAMPLE_SENTENCES[i]!r}")
            print(f"    [{j}] {SAMPLE_SENTENCES[j]!r}")

    # Discussion:
    # - Sentences [0] and [1] (cat/kitten on mat/rug) should have a notably
    #   higher similarity than either has with [2] (revenue growth), despite
    #   sharing almost no words.
    # - Normalizing first (a / ||a||, b / ||b||) makes ||a|| == ||b|| == 1,
    #   so the denominator (||a|| * ||b||) becomes 1 and
    #   cosine_similarity(a, b) reduces to just the dot product a . b.
    #   This is why examples/02_similarity_search.py normalizes vectors
    #   once at index-build time, then uses a plain matrix-vector product
    #   (index @ query_vector) for fast similarity search.


if __name__ == "__main__":
    main()
