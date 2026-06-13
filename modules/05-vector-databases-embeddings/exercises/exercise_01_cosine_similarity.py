"""
Exercise 1: Implement cosine similarity from scratch

TODO:
  1. Implement cosine_similarity(a, b) using only numpy.
  2. Verify it against TEST_VECTORS (identical, orthogonal, opposite).
  3. Use it to compare embeddings of SAMPLE_SENTENCES.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

# (name, vector_a, vector_b, expected_similarity)
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
    """
    TODO: implement cosine similarity between two 1D numpy vectors.

    cosine_similarity(a, b) = (a . b) / (||a|| * ||b||)
    """
    # return ...
    raise NotImplementedError


def main() -> None:
    print("=== Test vectors ===")
    for name, a, b, expected in TEST_VECTORS:
        # TODO: compute `result = cosine_similarity(a, b)` and compare to `expected`
        # print(f"{name}: got={result:.3f} expected={expected:.3f}")
        pass

    print("\n=== Sample sentences ===")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(SAMPLE_SENTENCES)

    # TODO: compute and print cosine_similarity for each pair of sentences
    # using your own implementation (not sklearn).
    for i in range(len(SAMPLE_SENTENCES)):
        for j in range(i + 1, len(SAMPLE_SENTENCES)):
            # similarity = cosine_similarity(embeddings[i], embeddings[j])
            # print(f"[{i}] vs [{j}]: {similarity:.3f}")
            pass


if __name__ == "__main__":
    main()
