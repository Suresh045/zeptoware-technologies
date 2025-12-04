# Resume Screening System (Flask + NLP + MySQL)

This is an AI-powered **Resume Screening System** built using **Flask**, **MySQL/SQLite**, and **Sentence-Transformers**.  
It allows candidates to upload resumes and HR to perform **semantic AI search** or **keyword search** across all resumes.

---

## 🚀 Features

### 👨‍🎓 Candidate
- Upload resume (PDF / DOCX)
- Automatic text extraction
- Automatic embedding generation using NLP

### 👩‍💼 HR
- **Semantic Search (AI Powered)**
- Keyword Search (Simple Mode)
- View full resume text
- Download original resume
- Recompute embeddings (optional)

---

## 🧠 Technologies Used

| Category | Technology |
|---------|------------|
| Backend | Flask (Python) |
| Database | **MySQL** (Primary) / SQLite (Optional) |
| NLP Model | all-MiniLM-L6-v2 (Sentence-Transformers) |
| ML Technique | Semantic Embedding + Cosine Similarity |
| Frontend | HTML, CSS |

---

---

## 📸 Project Screenshots

### 🧑‍🎓 Candidate — Upload Resume
<img src="https://raw.githubusercontent.com/Suresh045/zeptoware-technologies/main/screenshots/upload_page.png" width="800">

---

### 🧑‍💼 HR — Semantic Search (AI Mode)
<img src="https://raw.githubusercontent.com/Suresh045/zeptoware-technologies/main/screenshots/hr_semantic_search.png" width="800">

---

### 🔍 Semantic Search Results (Ranked by Similarity)
<img src="https://raw.githubusercontent.com/Suresh045/zeptoware-technologies/main/screenshots/semantic_results.png" width="800">

---

### 📝 Resume Viewer (Extracted Text)
<img src="https://raw.githubusercontent.com/Suresh045/zeptoware-technologies/main/screenshots/view_resume.png" width="800">

---

### 🧩 Keyword Search (Legacy Mode)
<img src="https://raw.githubusercontent.com/Suresh045/zeptoware-technologies/main/screenshots/keyword_search.png" width="800">

---

## 🗂️ Project Structure

```
resume_semantic_search_full/
├── app.py
├── config.py
├── models.py
├── utils.py
├── requirements.txt
├── README.md
├── resumes_semantic.db # created after first run (if using SQLite)
├── uploads/ # uploaded resumes
├── templates/
│ ├── base.html
│ ├── upload.html
│ ├── hr_search.html
│ ├── hr_search_semantic.html
│ ├── embed_all.html
│ ├── matches.html
│ └── view_resume.html
└── static/
└── style.css
```
---

# ⚙️ Setup & Installation

## 1️⃣ Clone the repository
```bash
git clone <your-repository-url>
cd resume-screening-system
```

---

# 🐬 MySQL Database Setup (Recommended)

### Create Database + User
```sql
CREATE DATABASE resume_db;
CREATE USER 'resume_user'@'localhost' IDENTIFIED BY 'Resume@123';
GRANT ALL PRIVILEGES ON resume_db.* TO 'resume_user'@'localhost';
FLUSH PRIVILEGES;
```

---

### Update `config.py` for MySQL
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://resume_user:Resume@123@localhost/resume_db"
UPLOAD_FOLDER = "uploads"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
```

---

### Install MySQL driver
```bash
pip install pymysql
```

---

# 🍃 (Optional) SQLite Mode

To use SQLite instead of MySQL:

```python
SQLALCHEMY_DATABASE_URI = "sqlite:///resumes_semantic.db"
```

No setup needed.

---

# 🧪 Virtual Environment Setup

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

Install Torch + SentenceTransformers:

```bash
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

---

# ▶️ Run the Application

```bash
python app.py
```

Open in browser:

- Upload Resume → http://127.0.0.1:5000/
- Keyword Search → /hr
- Semantic Search → /hr_semantic

---

# 🤖 How Semantic Search Works

1. Resume text is extracted using `pdfminer.six` / `python-docx`.  
2. Text is converted into a **384-dimension embedding** using:  
   **all-MiniLM-L6-v2 (Sentence-Transformers)**  
3. Job description is embedded the same way.  
4. **Cosine similarity** is used to score matches.  
5. Resumes are ranked from highest → lowest relevance.

---

# 🔍 Routes Summary

| Route | Purpose |
|-------|---------|
| `/` | Upload Resume |
| `/upload` | Save resume + generate embedding |
| `/hr` | Keyword search |
| `/search` | Process keyword search |
| `/hr_semantic` | Semantic search UI |
| `/search_semantic` | AI-based ranking |
| `/resume/<id>` | View resume text |
| `/embed_all` | Recompute embeddings |

---

# 🛠️ Troubleshooting

### ❌ Cannot import `cached_download`
Install compatible HuggingFace version:

```bash
pip install huggingface-hub==0.16.4
```

### ❌ MySQL “Access Denied”
Run:
```sql
ALTER USER 'resume_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Resume@123';
FLUSH PRIVILEGES;
```

### ❌ Semantic search slow
Use `/embed_all` to precompute embeddings.

---

# 📜 License
Open-source — you may use or modify this project freely.

---

# ❤️ Author
AI-based Resume Screening System using NLP + Deep Learning.
