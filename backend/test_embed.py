from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

text = "This PR adds support for the power operator to fix missing exponentiation."
embedding = model.encode(text)

print(type(embedding))
print(embedding.shape)
print(embedding[:5])