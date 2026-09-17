from agents.shared.embeddings import embedding_model
from agents.shared.vector_store import create_vector_store


texts = [
    "NeuroShield analyzes website privacy policies.",
    "The system checks websites for potential security risks.",
    "The weather forecast predicts tomorrow's temperature.",
]

vector_store = create_vector_store(texts, embedding_model)

results = vector_store.similarity_search(
    "What does NeuroShield do with privacy policies?",
    k=2,
)

print("Retrieved documents:")

for document in results:
    print("-", document.page_content)