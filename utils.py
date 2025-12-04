import os
import re
import json
from typing import List
import numpy as np
from config import ALLOWED_EXTENSIONS, EMBEDDING_MODEL_NAME
from pdfminer.high_level import extract_text as extract_text_from_pdf
from docx import Document
from sentence_transformers import SentenceTransformer

# ------------------------
# File helpers / extractors
# ------------------------

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_docx(path: str) -> str:
    try:
        doc = Document(path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print("docx parse error:", e)
        return ''

def extract_text(path: str) -> str:
    """
    Extract plain text from PDF or DOCX file.
    """
    ext = path.rsplit('.', 1)[1].lower()
    text = ''
    try:
        if ext == 'pdf':
            text = extract_text_from_pdf(path) or ''
        elif ext == 'docx':
            text = extract_text_from_docx(path) or ''
    except Exception as e:
        print('Error extracting text:', e)
    text = re.sub(r'\s+', ' ', text or '')
    return text.strip()

# ------------------------
# Embedding model (cached)
# ------------------------
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading SentenceTransformer model: {EMBEDDING_MODEL_NAME} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Model loaded.")
    return _model

def embed_texts(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """
    Returns numpy array of shape (len(texts), dim) with normalized embeddings.
    """
    model = get_embedding_model()
    embs = model.encode(texts, batch_size=batch_size, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
    return embs

# ------------------------
# Embedding serialization
# ------------------------

def embedding_to_json(emb: np.ndarray) -> str:
    return json.dumps(emb.tolist())

def json_to_embedding(s: str) -> np.ndarray:
    if not s:
        return None
    arr = json.loads(s)
    return np.array(arr, dtype=float)

# ------------------------
# Semantic ranking
# ------------------------

def semantic_rank(job_description: str, resume_objs, top_k: int = None):
    """
    Given a job_description and list of resume ORM objects, compute embedding for job_description,
    ensure resume embeddings exist (or compute on the fly), then compute cosine similarity.
    Returns list of dicts: {'resume': obj, 'score': float} sorted desc.
    """
    model = get_embedding_model()

    # job embedding (normalized)
    jd_emb = model.encode([job_description or ""], convert_to_numpy=True, normalize_embeddings=True)[0]

    # prepare list of embeddings for resumes (use existing if present)
    embeddings = []
    missing_indices = []     # indices of resumes missing embeddings
    missing_objs = []
    for i, r in enumerate(resume_objs):
        if r.embedding_json and r.embedding_json.strip():
            emb = json_to_embedding(r.embedding_json)
            if emb is None:
                missing_indices.append(i)
                missing_objs.append(r)
                embeddings.append(None)
            else:
                # ensure numpy float array
                emb = np.array(emb, dtype=float)
                # normalize to unit vector to be safe
                norm = np.linalg.norm(emb)
                if norm > 0:
                    emb = emb / norm
                embeddings.append(emb)
        else:
            missing_indices.append(i)
            missing_objs.append(r)
            embeddings.append(None)

    # compute embeddings for missing resumes in batch (if any)
    if missing_objs:
        texts_to_encode = [r.text_content or "" for r in missing_objs]
        try:
            new_embs = model.encode(texts_to_encode, convert_to_numpy=True, normalize_embeddings=True)
        except Exception as e:
            print("Error computing embeddings for missing resumes:", e)
            new_embs = np.zeros((len(missing_objs), jd_emb.shape[0]), dtype=float)
        # place them into embeddings list
        for idx, emb in zip(missing_indices, new_embs):
            embeddings[idx] = emb

    # build matrix and compute dot product (since normalized, dot == cosine)
    emb_matrix = np.vstack(embeddings) if len(embeddings) > 0 else np.zeros((0, jd_emb.shape[0]))
    if emb_matrix.shape[0] == 0:
        return []

    scores = np.dot(emb_matrix, jd_emb)  # shape (n_resumes,)
    matches = []
    for r, score in zip(resume_objs, scores.tolist()):
        matches.append({'resume': r, 'score': float(score)})
    matches.sort(key=lambda x: x['score'], reverse=True)
    if top_k:
        return matches[:top_k]
    return matches
