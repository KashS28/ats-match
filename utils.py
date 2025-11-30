import re

def clean_text(t: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s\.-]", " ", t).lower()

def tokenize(t: str):
    return re.findall(r"[a-zA-Z0-9]+", t)

def load_text(uploaded_file):
    import pdfplumber
    import docx2txt
    import io

    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    if uploaded_file.name.endswith(".docx"):
        return docx2txt.process(uploaded_file)

    return uploaded_file.read().decode("utf-8", errors="ignore")