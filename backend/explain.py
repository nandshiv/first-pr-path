import os
from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session
from embeddings import retrieve_relevant_chunks

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


FALLBACK_PHRASE = "The retrieved history doesn't contain a clear rationale for this file's design."

def explain_file(db: Session, repo_id: str, file_path: str):
    query = f"design decisions and reasoning about {file_path}"
    chunks = retrieve_relevant_chunks(db, repo_id, query, top_k=5)

    if len(chunks) == 0:
        return {
            "grounded": False,
            "explanation": "No historical discussion found for this file.",
            "sources": []
        }

    context_text = "\n\n---\n\n".join(
        f"[Source: {c.source_type} #{c.source_id}]\n{c.chunk_text}" for c in chunks
    )

    prompt = f"""You are explaining why a piece of code in an open-source project looks the way it does, to a first-time contributor.

Below are real historical PR/issue discussions related to the file "{file_path}". Using ONLY the information in these excerpts, explain the reasoning behind this file's design in 2-3 sentences.

If the excerpts don't actually explain any design reasoning, say exactly: "{FALLBACK_PHRASE}"

Do not invent or assume anything not present in the excerpts below.

{context_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    explanation_text = response.text.strip()
    actually_grounded = FALLBACK_PHRASE not in explanation_text

    return {
        "grounded": actually_grounded,
        "explanation": explanation_text,
        "sources": [{"type": c.source_type, "id": c.source_id} for c in chunks] if actually_grounded else []
    }