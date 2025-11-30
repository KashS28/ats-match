# app.py - BULLETPROOF VERSION
import re
import pdfplumber
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# Same stopwords as before
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
    'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their', 'our', 'your',
    'my', 'his', 'her', 'its', 'who', 'what', 'where', 'when', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'some', 'such',
    'no', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
    'just', 'now', 'then', 'also', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'between', 'under', 'again', 'further', 'once', 'here',
    'there', 'any', 'other', 'about', 'across', 'against', 'along',
    'among', 'around', 'behind', 'beside', 'besides', 'beyond', 'except',
    'inside', 'near', 'off', 'onto', 'outside', 'over', 'past', 'since',
    'toward', 'towards', 'unless', 'until', 'upon', 'within', 'without',
    'seeking', 'looking', 'opportunity', 'responsibilities', 'qualifications',
    'requirements', 'preferred', 'required', 'candidate', 'position', 'role',
    'job', 'work', 'experience', 'years', 'team', 'company', 'employees',
    'environment', 'culture', 'benefits', 'offer', 'competitive', 'excellent',
    'strong', 'ability', 'skills', 'knowledge', 'background', 'degree',
    'arrangements', 'diversity', 'features', 'solve', 'shaping', 'ambiguous',
    'complemented', 'thrive', 'scale', 'member', 'personalization', 'future',
    'task', 'tackle', 'people', 'addressing', 'performant', 'expand', 'leading',
    'comprehensive', 'fairness', 'diverse', 'build', 'voice', 'expertise',
    'individuals', 'initiatives', 'generous', 'architectures', 'fields', 'staff',
    'rapid', 'used', 'overall', 'recognized', 'improve', 'vision', 'incorporate',
    'process', 'develop', 'shared', 'provide', 'long', 'interests', 'interaction',
    'mainstream', 'direction', 'designing', 'scalability', 'define', 'skilled',
    'reasonable', 'drive', 'reliability', 'daily', 'dental', 'culture',
    'continuous', 'discord', 'text', 'junior', 'enhance', 'striving', 'online',
    'updated', 'feedback', 'world', 'connects', 'landscape', 'treated',
    'particularly', 'architectural', 'focus', 'ensuring', 'millions',
    'accommodations', 'building', 'meaningful', 'discipline', 'specializing',
    'contribute', 'policies', 'system', 'systems', 'developing', 'committed',
    'flexible', 'intuition', 'coverage', 'proficiency', 'entertainment', 'reach',
    'fostering', 'users', 'user', 'operate', 'problems', 'responsible', 'salary',
    'seamless', 'pivotal', 'foster', 'latest', 'multiplatform', 'complex',
    'effectively', 'discovery', 'mentor', 'join', 'applicants', 'wide',
    'efficiency', 'community', 'life', 'elevate', 'innovative', 'robustness',
    'cutting', 'solutions', 'leveraging', 'range', 'innovation', 'collaborate',
    'enable', 'boost', 'respect', 'friendships', 'office', 'continues', 'driven',
    'paid', 'advancements', 'technical', 'efforts', 'making', 'interview',
    'platform', 'deepen', 'inclusive', 'gaming', 'workplace', 'conception',
    'highly', 'disabilities', 'leave', 'utilizing', 'frameworks', 'recommendation',
    'impact', 'capable', 'stay', 'content', 'high', 'equity', 'edge',
    'connections', 'inclusion', 'employer', 'challenges', 'lead', 'options',
    'implementing', 'design', 'set', 'create', 'central', 'exciting', 'excellence',
    'communities', 'environments', 'tower', 'multi', 'communication', 'mission',
    'insurance', 'open', 'opportunities', 'term', 'extensive', 'equal', 'offers',
    'ended', 'integration', 'balance', 'influence', 'recommender', 'tools',
    'option', 'systemic', 'deploy', 'vibrant', 'values', 'balancing',
    'execution', 'time', 'performance', 'growth', 'engagement', 'data',
    'development', 'engineer', 'engineering', 'software', 'projects', 'project',
    'intelligence', 'health', 'social', 'remote', 'video', 'approach', 'cross',
    'real', 'iteration', 'san', 'francisco', 'master', 'science', 'dynamic',
    'support', 'based', 'standards', 'collaboration', 'power', 'robust',
    'production', 'applied', 'models', 'algorithms', 'scalable', 'digital',
    'functional', 'professional', 'techniques', 'related', 'deployment',
    'bachelor', 'bachelors', 'master', 'masters', 'phd', 'doctorate', 'degree',
    'b', 's', 'd', 'ph'
}

def load_resume_text(uploaded_file):
    """Load text from PDF, DOCX, or TXT file"""
    ext = uploaded_file.name.lower()
    if ext.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])
    elif ext.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")

MONTHS_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12,
}

DATE_PATTERN = re.compile(r"(?P<month>[A-Za-z]{3,9}|\d{1,2})[,\s]*(?P<year>\d{4})", re.IGNORECASE)

def convert_date(text):
    """Convert 'May 2025' to YYYY-MM"""
    text = text.lower().strip()
    if text in ["present", "current", "now"]:
        return "Present"
    m = DATE_PATTERN.search(text)
    if not m:
        return None
    month_raw = m.group("month").lower()
    year = m.group("year")
    if month_raw.isdigit() and 1 <= int(month_raw) <= 12:
        month = int(month_raw)
    else:
        month = MONTHS_MAP.get(month_raw[:3], None)
    if not month:
        return None
    return f"{year}-{month:02d}"

def compute_months(start, end):
    """Compute months between dates"""
    if not start:
        return 0
    if not end or end == "Present":
        now = datetime.now()
        end = f"{now.year}-{now.month:02d}"
    try:
        sy, sm = map(int, start.split("-"))
        ey, em = map(int, end.split("-"))
        return max(0, (ey - sy) * 12 + (em - sm))
    except:
        return 0

def parse_resume_to_json(text):
    """
    BULLETPROOF parser - handles ALL resume formats
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    # Find section indices
    sections = {"experience": None, "education": None, "projects": None, "skills": None}
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        # Match section headers (must be short and exact match)
        if len(line) < 30:
            if re.match(r"^experience\s*$", line_lower):
                sections["experience"] = i
            elif re.match(r"^education\s*$", line_lower):
                sections["education"] = i
            elif re.match(r"^projects?\s*$", line_lower):
                sections["projects"] = i
            elif re.match(r"^skills?\s*$", line_lower):
                sections["skills"] = i
    
    experience = []
    education = []
    projects = []
    skills = []
    
    # ========== EXPERIENCE ==========
    if sections["experience"] is not None:
        start_idx = sections["experience"] + 1
        
        # Find end of experience section
        end_idx = len(lines)
        for section, idx in sections.items():
            if section != "experience" and idx is not None and idx > start_idx:
                end_idx = min(end_idx, idx)
        
        exp_lines = lines[start_idx:end_idx]
        
        current = {"company": "", "title": "", "start_date": None, "end_date": None, "bullets": [], "employment_type": "FT"}
        
        for line in exp_lines:
            # Check if line has a 4-digit year (likely a job header)
            has_year = bool(re.search(r"\b\d{4}\b", line))
            is_bullet = line.startswith(("•", "-", "â€¢", "*", "·", "–"))
            
            if has_year and not is_bullet:
                # Save previous entry
                if current["company"] or current["title"]:
                    current["months"] = compute_months(current["start_date"], current["end_date"])
                    experience.append(current)
                
                # New job entry
                current = {"company": "", "title": "", "start_date": None, "end_date": None, "bullets": [], "employment_type": "FT"}
                
                # Try multiple parsing strategies
                
                # Strategy 1: "Company - Title (Date - Date)"
                if " - " in line:
                    parts = line.split(" - ", 1)
                    current["company"] = parts[0].strip()
                    rest = parts[1]
                    
                    # Find date portion
                    date_match = re.search(r"[\(\|]?\s*([A-Za-z]+\s+\d{4})", rest)
                    if date_match:
                        date_start = date_match.start()
                        current["title"] = rest[:date_start].strip()
                        date_portion = rest[date_start:]
                        
                        # Extract all dates
                        all_dates = re.findall(DATE_PATTERN, date_portion)
                        if len(all_dates) >= 1:
                            current["start_date"] = convert_date(" ".join(all_dates[0]))
                        if len(all_dates) >= 2:
                            current["end_date"] = convert_date(" ".join(all_dates[1]))
                        elif "present" in date_portion.lower():
                            current["end_date"] = "Present"
                    else:
                        current["title"] = rest.strip()
                
                # Strategy 2: Just parse whatever we can
                else:
                    # Extract dates from line
                    all_dates = re.findall(DATE_PATTERN, line)
                    if all_dates:
                        if len(all_dates) >= 1:
                            current["start_date"] = convert_date(" ".join(all_dates[0]))
                        if len(all_dates) >= 2:
                            current["end_date"] = convert_date(" ".join(all_dates[1]))
                        elif "present" in line.lower():
                            current["end_date"] = "Present"
                    
                    # Everything before first date is title/company
                    first_date_match = re.search(r"\d{4}", line)
                    if first_date_match:
                        before_date = line[:first_date_match.start()].strip()
                        # Try to split into company and title
                        if " - " in before_date:
                            parts = before_date.split(" - ", 1)
                            current["company"] = parts[0].strip()
                            current["title"] = parts[1].strip()
                        else:
                            current["title"] = before_date
            
            elif is_bullet:
                bullet_text = line.lstrip("•-â€¢*·– ").strip()
                if bullet_text:
                    current["bullets"].append(bullet_text)
        
        # Save last entry
        if current["company"] or current["title"]:
            current["months"] = compute_months(current["start_date"], current["end_date"])
            experience.append(current)
    
    # ========== EDUCATION ==========
    if sections["education"] is not None:
        start_idx = sections["education"] + 1
        end_idx = len(lines)
        for section, idx in sections.items():
            if section != "education" and idx is not None and idx > start_idx:
                end_idx = min(end_idx, idx)
        
        edu_lines = lines[start_idx:end_idx]
        current = {"institution": "", "degree": "", "graduation_date": None, "gpa": None, "courses": []}
        
        for line in edu_lines:
            if any(word in line.lower() for word in ["university", "college", "institute", "school"]):
                if current["institution"]:
                    education.append(current)
                current = {"institution": "", "degree": "", "graduation_date": None, "gpa": None, "courses": []}
                
                if " - " in line:
                    parts = line.split(" - ", 1)
                    current["institution"] = parts[0].strip()
                    current["degree"] = parts[1].strip()
                else:
                    current["institution"] = line.strip()
            
            elif "gpa" in line.lower():
                gpa_match = re.search(r"(\d\.\d+)", line)
                if gpa_match:
                    current["gpa"] = float(gpa_match.group(1))
            
            elif any(word in line.lower() for word in ["bachelor", "master", "phd", "degree", "b.s", "m.s"]):
                if not current["degree"]:
                    current["degree"] = line.strip()
            
            elif "course" in line.lower():
                if ":" in line:
                    courses_text = line.split(":", 1)[1]
                    current["courses"] = [c.strip() for c in re.split(r"[,;]", courses_text) if c.strip()]
        
        if current["institution"]:
            education.append(current)
    
    # ========== PROJECTS ==========
    if sections["projects"] is not None:
        start_idx = sections["projects"] + 1
        end_idx = len(lines)
        for section, idx in sections.items():
            if section != "projects" and idx is not None and idx > start_idx:
                end_idx = min(end_idx, idx)
        
        proj_lines = lines[start_idx:end_idx]
        current = {"title": "", "bullets": []}
        
        for line in proj_lines:
            is_bullet = line.startswith(("•", "-", "â€¢", "*", "·", "–"))
            
            if not is_bullet and len(line) > 10:
                if current["title"]:
                    projects.append(current)
                current = {"title": line.strip(), "bullets": []}
            elif is_bullet:
                bullet_text = line.lstrip("•-â€¢*·– ").strip()
                if bullet_text:
                    current["bullets"].append(bullet_text)
        
        if current["title"]:
            projects.append(current)
    
    # ========== SKILLS ==========
    if sections["skills"] is not None:
        start_idx = sections["skills"] + 1
        skill_lines = []
        for i in range(start_idx, min(start_idx + 10, len(lines))):
            line = lines[i]
            if len(line) < 50 and any(section in line.lower() for section in ["experience", "education", "project"]):
                break
            skill_lines.append(line)
        
        combined = " ".join(skill_lines)
        combined = re.sub(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:', '', combined)
        skill_list = re.split(r"[,;|•\n]", combined)
        skill_list = [s.strip() for s in skill_list if s.strip()]
        
        filtered_skills = []
        for skill in skill_list:
            if len(skill) < 2 or len(skill) > 50:
                continue
            if re.search(r'\d+%', skill):
                continue
            if any(word in skill.lower() for word in [' by ', ' for ', ' and enabling', ' using ']):
                continue
            filtered_skills.append(skill)
        
        skills = filtered_skills
    
    return {
        "experience": experience,
        "education": education,
        "projects": projects,
        "skills": {"all": skills},
    }

def extract_technical_skills(text):
    """Extract ONLY technical skills"""
    text_lower = text.lower()
    tokens = set(re.findall(r"[a-zA-Z0-9\+\#\.]+", text_lower))
    technical_skills = {t for t in tokens if t not in STOPWORDS}
    technical_skills = {t for t in technical_skills if not t.isdigit()}
    known_short = {'c', 'r', 'go', 'c++', 'c#'}
    technical_skills = {t for t in technical_skills if len(t) > 2 or t in known_short}
    return technical_skills

def compute_skill_match(jd, resume_text):
    """Compute skill match"""
    jd_skills = extract_technical_skills(jd)
    resume_skills = extract_technical_skills(resume_text)
    overlap = list(jd_skills & resume_skills)
    missing = list(jd_skills - resume_skills)
    
    if len(jd_skills) == 0:
        return {"score": 0, "overlap": [], "missing": []}
    
    keyword_match_pct = (len(overlap) / len(jd_skills)) * 100
    
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        tfidf = vectorizer.fit_transform([jd.lower(), resume_text.lower()])
        semantic_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        final_score = (keyword_match_pct * 0.7) + (semantic_sim * 100 * 0.3)
    except:
        final_score = keyword_match_pct
    
    return {"score": round(final_score, 2), "overlap": sorted(overlap), "missing": sorted(missing)}

def extract_min_years(jd_text):
    """Extract minimum years"""
    matches = re.findall(r"(\d+)\+?\s+years?", jd_text.lower())
    if matches:
        return int(matches[0])
    return 0

def estimate_seniority(months):
    """Estimate seniority"""
    if months < 24:
        return "Junior"
    elif months < 60:
        return "Mid"
    return "Senior"
