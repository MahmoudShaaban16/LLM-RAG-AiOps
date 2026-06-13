"""
01 - Generate Embeddings

Demonstrates:
  1. Turning sentences into embedding vectors with a small local model
     (sentence-transformers/all-MiniLM-L6-v2 — no API key required).
  2. Inspecting the dimensionality of the resulting vectors.
  3. Computing pairwise cosine similarity to show that semantically
     similar sentences end up close together in vector space.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "all-MiniLM-L6-v2"

SENTENCES = [
    "The cat sat on the mat.",
    "A kitten rested on a rug.",
    "Quarterly revenue grew by 12% year over year.",
    "Our sales increased twelve percent compared to last year.",
    "I love hiking in the mountains on weekends.",
]


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(SENTENCES)

    print(f"Model: {MODEL_NAME}")
    print(f"Number of sentences: {len(SENTENCES)}")
    print(f"Embedding dimensionality: {embeddings.shape[1]}")
    print()

    # Pairwise cosine similarity matrix
    similarity_matrix = cosine_similarity(embeddings)

    print("Pairwise cosine similarity:")
    print()
    header = "".join(f"{i:>8}" for i in range(len(SENTENCES)))
    print(f"{'':4}{header}")
    for i, row in enumerate(similarity_matrix):
        row_str = "".join(f"{value:8.3f}" for value in row)
        print(f"[{i}]{row_str}")

    print()
    print("Sentences:")
    for i, sentence in enumerate(SENTENCES):
        print(f"  [{i}] {sentence}")

    print()
    print("Observation: sentences [0] and [1] (both about a cat/kitten on a")
    print("mat/rug) and sentences [2] and [3] (both about revenue growth)")
    print("have high similarity scores despite sharing almost no words —")
    print("because the embedding captures *meaning*, not just vocabulary.")


if __name__ == "__main__":
    main()
