# app.py
import re
import pdfplumber
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------------------------------
# 1. LOAD TEXT FROM RESUME FILE
# -----------------------------------------------------------
def load_resume_text(uploaded_file):
    ext = uploaded_file.name.lower()

    if ext.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])

    elif ext.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])

    else:  # TXT
        return uploaded_file.read().decode("utf-8", errors="ignore")


# -----------------------------------------------------------
# 2. PARSE RESUME INTO STRUCTURED JSON
# -----------------------------------------------------------

MONTHS_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

DATE_PATTERN = re.compile(
    r"(?P<month>[A-Za-z]{3,9}|\d{1,2})\s*(?P<year>\d{4})",
    re.IGNORECASE
)

def convert_date(text):
    """
    Convert textual dates like 'Aug 2024', 'August 2024', '8 2024' to YYYY-MM.
    """
    text = text.lower().strip()

    if text == "present":
        return "Present"

    m = DATE_PATTERN.search(text)
    if not m:
        return None

    month_raw = m.group("month").lower()
    year = m.group("year")

    # numeric month
    if month_raw.isdigit() and 1 <= int(month_raw) <= 12:
        month = int(month_raw)
    else:
        month = MONTHS_MAP.get(month_raw[:3], None)

    if not month:
        return None

    return f"{year}-{month:02d}"

def compute_months(start, end):
    """Compute months between YYYY-MM and YYYY-MM."""
    if not start or not end or end == "Present":
        return 0

    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))

    return max(0, (ey - sy) * 12 + (em - sm))


def parse_resume_to_json(text):
    """
    Very strong structured parser for Experience, Education, Projects, Skills.
    """

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    experience = []
    education = []
    projects = []
    skills = []

    # -------- EXPERIENCE --------
    exp_idx = [i for i, l in enumerate(lines) if "experience" in l.lower()]
    if exp_idx:
        start = exp_idx[0] + 1
        # stop before next section
        end = min(
            [i for i, l in enumerate(lines) if any(x in l.lower() for x in ["education", "project", "skill"]) and i > start]
            or [len(lines)]
        )
        exp_block = lines[start:end]

        current = {"company": "", "title": "", "start_date": None, "end_date": None, "bullets": []}

        for l in exp_block:
            # Detect role line with date span
            date_span = re.search(r"(.+?)\s+(?:–|-)\s+(.+)", l)
            if date_span:
                # save old
                if current["title"] or current["company"]:
                    experience.append(current)
                current = {"company": "", "title": "", "start_date": None, "end_date": None, "bullets": []}

                text_left = date_span.group(1)
                text_right = date_span.group(2)

                # Split text_left: Company + Role
                if "-" in text_left:
                    parts = text_left.split("-", 1)
                    current["company"] = parts[0].strip()
                    current["title"] = parts[1].strip()
                else:
                    current["title"] = text_left.strip()

                # Dates
                dates = re.findall(DATE_PATTERN, l)
                if len(dates) >= 1:
                    current["start_date"] = convert_date(" ".join(dates[0]))
                if len(dates) >= 2:
                    current["end_date"] = convert_date(" ".join(dates[1]))
                else:
                    if "present" in l.lower():
                        current["end_date"] = "Present"

            elif l.startswith("•") or l.startswith("-"):
                current["bullets"].append(l.lstrip("•- ").strip())

        if current["title"] or current["company"]:
            experience.append(current)

    # Compute months
    for e in experience:
        e["months"] = compute_months(e.get("start_date"), e.get("end_date"))

    # -------- EDUCATION --------
    edu_idx = [i for i, l in enumerate(lines) if "education" in l.lower()]
    if edu_idx:
        start = edu_idx[0] + 1
        end = min(
            [i for i, l in enumerate(lines) if "project" in l.lower() and i > start]
            or [len(lines)]
        )
        edu_block = lines[start:end]

        current = {"institution": "", "degree": "", "graduation_date": None, "gpa": None, "courses": []}

        for l in edu_block:
            if "university" in l.lower() or "institute" in l.lower():
                if current["institution"]:
                    education.append(current)
                current = {"institution": l, "degree": "", "graduation_date": None, "gpa": None, "courses": []}

            elif "gpa" in l.lower():
                g = re.findall(r"(\d\.\d+)", l)
                if g:
                    current["gpa"] = float(g[0])

            elif any(word in l.lower() for word in ["bachelor", "master"]):
                current["degree"] = l

            elif "course" in l.lower():
                parts = l.split(":")
                if len(parts) > 1:
                    current["courses"] = [c.strip() for c in parts[1].split(",")]

        if current["institution"]:
            education.append(current)

    # -------- PROJECTS --------
    proj_idx = [i for i, l in enumerate(lines) if "project" in l.lower()]
    if proj_idx:
        start = proj_idx[0] + 1
        proj_block = lines[start:]

        current = {"title": "", "bullets": []}
        for l in proj_block:
            if l.lower().startswith("project"):
                # save previous
                if current["title"]:
                    projects.append(current)
                current = {"title": l, "bullets": []}

            elif l.startswith("•") or l.startswith("-"):
                current["bullets"].append(l.lstrip("•- ").strip())

        if current["title"]:
            projects.append(current)

    # -------- SKILLS --------
    skill_idx = [i for i, l in enumerate(lines) if "skill" in l.lower()]
    if skill_idx:
        start = skill_idx[0] + 1
        skill_block = lines[start:start + 3]  # usually few lines
        combined = " ".join(skill_block)
        skill_list = re.split(r"[,|•|-]\s*", combined)
        skill_list = [s.strip() for s in skill_list if s.strip()]
        skills = list(set(skill_list))

    return {
        "experience": experience,
        "education": education,
        "projects": projects,
        "skills": {"all": skills},
    }


# -----------------------------------------------------------
# 3. SKILL MATCHING (TF-IDF semantic + direct overlap)
# -----------------------------------------------------------
def compute_skill_match(jd, resume_text):
    jd_clean = jd.lower()
    resume_clean = resume_text.lower()

    jd_words = set(re.findall(r"[a-zA-Z0-9\+\#]+", jd_clean))
    resume_words = set(re.findall(r"[a-zA-Z0-9\+\#]+", resume_clean))

    overlap = list(jd_words & resume_words)
    missing = list(jd_words - resume_words)

    if len(jd_clean) < 20:
        return {"score": 0, "overlap": overlap, "missing": missing}

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([jd_clean, resume_clean])
    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

    score = round(sim * 100, 2)

    return {"score": score, "overlap": overlap, "missing": missing}


# -----------------------------------------------------------
# 4. MIN YEARS OF EXPERIENCE EXTRACTOR
# -----------------------------------------------------------
def extract_min_years(jd_text):
    """
    Extract 'X years of experience' from JD.
    """
    jd = jd_text.lower()
    matches = re.findall(r"(\d+)\+?\s+years?", jd)
    if matches:
        return int(matches[0])
    return 0


# -----------------------------------------------------------
# 5. SENIORITY ESTIMATOR
# -----------------------------------------------------------
def estimate_seniority(months):
    if months < 24:
        return "Junior"
    elif months < 60:
        return "Mid"
    return "Senior"