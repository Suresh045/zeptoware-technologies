import os
from flask import Flask, request, redirect, url_for, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Resume
# add these imports near other imports in app.py
from utils import allowed_file, extract_text, semantic_rank, get_embedding_model, embed_texts, embedding_to_json
from config import UPLOAD_FOLDER, SQLALCHEMY_DATABASE_URI, MAX_CONTENT_LENGTH, FLASK_SECRET
import json

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = FLASK_SECRET
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Database setup
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# ---- Routes ----

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    file = request.files.get('resume')
    name = request.form.get('name')
    email = request.form.get('email')
    if not file or file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    if not allowed_file(file.filename):
        flash('File type not allowed. Only PDF and DOCX are accepted.')
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    base, ext = os.path.splitext(filename)
    counter = 1
    # avoid overwrite
    while os.path.exists(saved_path):
        filename = f"{base}_{counter}{ext}"
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter += 1

    file.save(saved_path)

    # extract text
    text = extract_text(saved_path)

    # try to compute embedding immediately (synchronous)
    emb_json = None
    try:
        # embed_texts returns a numpy array; batch_size=1 for single doc
        emb_array = embed_texts([text], batch_size=1)[0]
        emb_json = embedding_to_json(emb_array)
    except Exception as e:
        # if embedding fails, log and continue — resume will be saved without embedding
        print("Warning: embedding compute failed on upload:", repr(e))
        emb_json = None

    # save to DB (embedding_json saved if computed)
    session = SessionLocal()
    resume = Resume(
        filename=filename,
        filepath=saved_path,
        text_content=text,
        candidate_name=name,
        candidate_email=email,
        embedding_json=emb_json
    )
    session.add(resume)
    session.commit()
    session.close()

    flash('Resume uploaded successfully')
    return redirect(url_for('index'))


@app.route('/hr')
def hr_search_page():
    return render_template('hr_search.html')

@app.route('/hr_semantic')
def hr_search_semantic_page():
    return render_template('hr_search_semantic.html')


@app.route('/search', methods=['POST'])
def search_keywords():
    keywords = request.form.get('keywords', '')
    mode = request.form.get('mode', 'any')

    if not keywords:
        flash('Please enter keywords')
        return redirect(url_for('hr_search_page'))

    # Split keywords by comma
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]

    session = SessionLocal()
    resumes = session.query(Resume).all()

    # Simple keyword matching
    results = []
    for r in resumes:
        text = r.text_content.lower()
        count = 0
        for k in keyword_list:
            if k.lower() in text:
                count += 1

        if (mode == 'all' and count == len(keyword_list)) or \
           (mode == 'any' and count > 0):
            results.append({'resume': r, 'score': count})

    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)

    session.close()

    return render_template('matches.html', matches=results, keywords=keyword_list)


@app.route('/search_semantic', methods=['POST'])
def search_semantic():
    job_description = request.form.get('job_description', '').strip()
    if not job_description:
        flash('Provide a job description or keywords for semantic search.')
        return redirect(url_for('hr_search_semantic_page'))

    session = SessionLocal()
    resumes = session.query(Resume).all()

    # compute semantic ranking (this will compute embeddings for missing resumes in memory)
    matches = semantic_rank(job_description, resumes)

    # persist missing embeddings for resumes that lacked them (so next searches are faster)
    missing = [r for r in resumes if not r.embedding_json or not r.embedding_json.strip()]
    if missing:
        model = get_embedding_model()
        texts = [r.text_content or '' for r in missing]
        try:
            embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            for r, emb in zip(missing, embs):
                r.embedding_json = embedding_to_json(emb)
                session.merge(r)
            session.commit()
        except Exception as e:
            print("Warning: could not persist embeddings:", e)
    session.close()

    return render_template('matches.html', matches=matches, keywords=[job_description])



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/view/<int:resume_id>')
def view_resume(resume_id):
    session = SessionLocal()
    r = session.query(Resume).filter(Resume.id == resume_id).first()
    session.close()
    if not r:
        flash('Resume not found')
        return redirect(url_for('hr_search_page'))
    return render_template('view_resume.html', resume=r)

if __name__ == '__main__':
    # Ensure DB and tables exist
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)
