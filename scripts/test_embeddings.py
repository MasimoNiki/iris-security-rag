from app.services.embeddings.provider import SentenceTransformerEmbeddingProvider


def main() -> None:
    provider = SentenceTransformerEmbeddingProvider()

    query = "Что делать при phishing alert?"
    vector = provider.embed_query(query)

    print(f"Model: {provider.model_name}")
    print(f"Vector dimension: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")


if __name__ == "__main__":
    main()
