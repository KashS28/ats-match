# app.py - PRODUCTION READY VERSION
import re
import pdfplumber
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# -----------------------------------------------------------
# COMPREHENSIVE STOPWORDS - Filters out ALL filler words
# -----------------------------------------------------------
STOPWORDS = {
    # Articles, prepositions, conjunctions
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
    'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    
    # Pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their', 'our', 'your',
    'my', 'his', 'her', 'its', 'who', 'what', 'where', 'when', 'why', 'how',
    
    # Common words
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'some', 'such',
    'no', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
    'just', 'now', 'then', 'also', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'between', 'under', 'again', 'further', 'once', 'here',
    'there', 'any', 'other', 'about', 'across', 'against', 'along',
    'among', 'around', 'behind', 'beside', 'besides', 'beyond', 'except',
    'inside', 'near', 'off', 'onto', 'outside', 'over', 'past', 'since',
    'toward', 'towards', 'unless', 'until', 'upon', 'within', 'without',
    
    # JD boilerplate
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
    
    # Generic terms that appear everywhere
    'execution', 'time', 'performance', 'growth', 'engagement', 'data',
    'development', 'engineer', 'engineering', 'software', 'projects', 'project',
    'intelligence', 'health', 'social', 'remote', 'video', 'approach', 'cross',
    'real', 'iteration', 'san', 'francisco', 'master', 'science', 'dynamic',
    'support', 'based', 'standards', 'collaboration', 'power', 'robust',
    'production', 'applied', 'models', 'algorithms', 'scalable', 'digital',
    'functional', 'professional', 'techniques', 'related', 'deployment',
    
    # Degree levels (not technical skills)
    'bachelor', 'bachelors', 'master', 'masters', 'phd', 'doctorate', 'degree',
    'b', 's', 'd', 'ph'
}

# -----------------------------------------------------------
# 1. LOAD TEXT FROM RESUME FILE
# -----------------------------------------------------------
def load_resume_text(uploaded_file):
    """Load text from PDF, DOCX, or TXT file"""
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
# 2. DATE HANDLING
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
    r"(?P<month>[A-Za-z]{3,9}|\d{1,2})[,\s]*(?P<year>\d{4})",
    re.IGNORECASE
)

def convert_date(text):
    """Convert 'May 2025', 'Aug 2024', etc. to YYYY-MM format"""
    text = text.lower().strip()

    if text in ["present", "current", "now"]:
        return "Present"

    m = DATE_PATTERN.search(text)
    if not m:
        return None

    month_raw = m.group("month").lower()
    year = m.group("year")

    # Handle numeric month
    if month_raw.isdigit() and 1 <= int(month_raw) <= 12:
        month = int(month_raw)
    else:
        month = MONTHS_MAP.get(month_raw[:3], None)

    if not month:
        return None

    return f"{year}-{month:02d}"

def compute_months(start, end):
    """Compute months between two dates, handling 'Present'"""
    if not start:
        return 0
    
    # If end is Present or None, use current date
    if not end or end == "Present":
        now = datetime.now()
        end = f"{now.year}-{now.month:02d}"
    
    try:
        sy, sm = map(int, start.split("-"))
        ey, em = map(int, end.split("-"))
        return max(0, (ey - sy) * 12 + (em - sm))
    except:
        return 0


# -----------------------------------------------------------
# 3. RESUME PARSING - COMPLETELY REWRITTEN
# -----------------------------------------------------------

def parse_resume_to_json(text):
    """
    Parse resume with proper company/title extraction and section detection
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    experience = []
    education = []
    projects = []
    skills = []

    # -------- EXPERIENCE --------
    exp_idx = None
    for i, l in enumerate(lines):
        if re.match(r"^experience\s*$", l.lower()):
            exp_idx = i
            break
    
    if exp_idx is not None:
        start = exp_idx + 1
        
        # Find where experience section ends
        next_section_idx = len(lines)
        for i in range(start, len(lines)):
            line_lower = lines[i].lower()
            if (len(lines[i]) < 50 and 
                any(section in line_lower for section in ["education", "project", "skill"])):
                next_section_idx = i
                break
        
        exp_block = lines[start:next_section_idx]
        
        current = {
            "company": "",
            "title": "",
            "start_date": None,
            "end_date": None,
            "bullets": [],
            "employment_type": "FT"
        }
        
        for line in exp_block:
            # Check if this line contains a date (likely a job header)
            has_date = bool(re.search(r"\d{4}", line))
            
            if has_date and len(line) > 10:
                # Save previous entry
                if current["title"] or current["company"]:
                    current["months"] = compute_months(
                        current["start_date"], 
                        current["end_date"]
                    )
                    experience.append(current)
                
                # Start new entry
                current = {
                    "company": "",
                    "title": "",
                    "start_date": None,
                    "end_date": None,
                    "bullets": [],
                    "employment_type": "FT"
                }
                
                # Parse: "Company - Title (Date - Date)" or "Company - Title | Date - Date"
                if " - " in line:
                    parts = line.split(" - ", 1)
                    current["company"] = parts[0].strip()
                    rest = parts[1]
                    
                    # Find where dates start
                    date_match = re.search(r"\(|\||\d{4}", rest)
                    if date_match:
                        # Everything before dates is the title
                        title_text = rest[:date_match.start()].strip()
                        current["title"] = title_text
                        
                        # Extract dates from the rest
                        dates_portion = rest[date_match.start():]
                        dates = re.findall(DATE_PATTERN, dates_portion)
                        
                        if len(dates) >= 1:
                            current["start_date"] = convert_date(" ".join(dates[0]))
                        if len(dates) >= 2:
                            current["end_date"] = convert_date(" ".join(dates[1]))
                        elif "present" in dates_portion.lower():
                            current["end_date"] = "Present"
                    else:
                        current["title"] = rest.strip()
                else:
                    # No " - " separator, try to extract what we can
                    current["title"] = line.strip()
            
            # Bullet point
            elif line.startswith(("•", "-", "â€¢", "*", "·")):
                bullet_text = line.lstrip("•-â€¢*· ").strip()
                if bullet_text:
                    current["bullets"].append(bullet_text)
        
        # Save last entry
        if current["title"] or current["company"]:
            current["months"] = compute_months(
                current["start_date"],
                current["end_date"]
            )
            experience.append(current)

    # -------- EDUCATION --------
    edu_idx = None
    for i, l in enumerate(lines):
        if re.match(r"^education\s*$", l.lower()):
            edu_idx = i
            break
    
    if edu_idx is not None:
        start = edu_idx + 1
        
        # Find where education section ends
        next_section_idx = len(lines)
        for i in range(start, len(lines)):
            line_lower = lines[i].lower()
            if (len(lines[i]) < 50 and 
                any(section in line_lower for section in ["experience", "project", "skill"])):
                next_section_idx = i
                break
        
        edu_block = lines[start:next_section_idx]
        
        current = {
            "institution": "",
            "degree": "",
            "graduation_date": None,
            "gpa": None,
            "courses": []
        }
        
        for line in edu_block:
            # Institution line (has university/college/institute)
            if any(word in line.lower() for word in ["university", "college", "institute", "school"]):
                # Save previous entry if it has institution
                if current["institution"]:
                    education.append(current)
                
                current = {
                    "institution": "",
                    "degree": "",
                    "graduation_date": None,
                    "gpa": None,
                    "courses": []
                }
                
                # Parse "Institution - Degree" or just "Institution"
                if " - " in line:
                    parts = line.split(" - ", 1)
                    current["institution"] = parts[0].strip()
                    current["degree"] = parts[1].strip()
                else:
                    current["institution"] = line.strip()
            
            # GPA line
            elif "gpa" in line.lower():
                gpa_match = re.search(r"(\d\.\d+)", line)
                if gpa_match:
                    current["gpa"] = float(gpa_match.group(1))
            
            # Degree line
            elif any(word in line.lower() for word in ["bachelor", "master", "phd", "degree", "b.s", "m.s"]):
                if not current["degree"]:
                    current["degree"] = line.strip()
            
            # Coursework line
            elif "course" in line.lower():
                if ":" in line:
                    courses_text = line.split(":", 1)[1]
                    current["courses"] = [c.strip() for c in re.split(r"[,;]", courses_text) if c.strip()]
        
        # Save last entry if it has institution
        if current["institution"]:
            education.append(current)

    # -------- PROJECTS --------
    proj_idx = None
    for i, l in enumerate(lines):
        if re.match(r"^project", l.lower()):
            proj_idx = i
            break
    
    if proj_idx is not None:
        start = proj_idx + 1
        
        # Find where projects section ends
        next_section_idx = len(lines)
        for i in range(start, len(lines)):
            line_lower = lines[i].lower()
            if (len(lines[i]) < 50 and 
                any(section in line_lower for section in ["experience", "education", "skill"])):
                next_section_idx = i
                break
        
        proj_block = lines[start:next_section_idx]
        
        current = {"title": "", "bullets": []}
        
        for line in proj_block:
            # Project title (not a bullet, longer than 10 chars)
            if not line.startswith(("•", "-", "â€¢", "*", "·")) and len(line) > 10:
                # Save previous if it has title
                if current["title"]:
                    projects.append(current)
                current = {"title": line.strip(), "bullets": []}
            
            # Bullet point
            elif line.startswith(("•", "-", "â€¢", "*", "·")):
                bullet_text = line.lstrip("•-â€¢*· ").strip()
                if bullet_text:
                    current["bullets"].append(bullet_text)
        
        # Save last entry if it has title
        if current["title"]:
            projects.append(current)

    # -------- SKILLS --------
    skill_idx = None
    for i, l in enumerate(lines):
        if re.match(r"^skill", l.lower()):
            skill_idx = i
            break
    
    if skill_idx is not None:
        start = skill_idx + 1
        
        # Skills usually span just a few lines
        skill_lines = []
        for i in range(start, min(start + 10, len(lines))):
            line = lines[i]
            # Stop if we hit another section
            if (len(line) < 50 and 
                any(section in line.lower() for section in ["experience", "education", "project"])):
                break
            skill_lines.append(line)
        
        # Combine all skill lines
        combined = " ".join(skill_lines)
        
        # Remove category headers like "Programming Languages:", "ML and Data Science:"
        combined = re.sub(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:', '', combined)
        
        # Split by common delimiters
        skill_list = re.split(r"[,;|•\n]", combined)
        skill_list = [s.strip() for s in skill_list if s.strip()]
        
        # Filter out junk
        filtered_skills = []
        for skill in skill_list:
            # Skip if too short
            if len(skill) < 2:
                continue
            # Skip if contains numbers followed by %
            if re.search(r'\d+%', skill):
                continue
            # Skip if too long (likely a sentence)
            if len(skill) > 50:
                continue
            # Skip if looks like a sentence (has verbs)
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


# -----------------------------------------------------------
# 4. TECHNICAL SKILLS EXTRACTION
# -----------------------------------------------------------

def extract_technical_skills(text):
    """Extract ONLY technical skills, filter out all stopwords"""
    text_lower = text.lower()
    
    # Extract alphanumeric tokens (including C++, C#, Node.js, etc.)
    tokens = set(re.findall(r"[a-zA-Z0-9\+\#\.]+", text_lower))
    
    # Filter out stopwords
    technical_skills = {t for t in tokens if t not in STOPWORDS}
    
    # Filter out pure numbers
    technical_skills = {t for t in technical_skills if not t.isdigit()}
    
    # Filter out very short tokens (except known languages)
    known_short = {'c', 'r', 'go', 'c++', 'c#'}
    technical_skills = {t for t in technical_skills if len(t) > 2 or t in known_short}
    
    return technical_skills

def compute_skill_match(jd, resume_text):
    """Compute skill match using ONLY technical skills"""
    jd_skills = extract_technical_skills(jd)
    resume_skills = extract_technical_skills(resume_text)
    
    # Find overlaps
    overlap = list(jd_skills & resume_skills)
    missing = list(jd_skills - resume_skills)
    
    # Calculate match percentage
    if len(jd_skills) == 0:
        return {"score": 0, "overlap": [], "missing": []}
    
    keyword_match_pct = (len(overlap) / len(jd_skills)) * 100
    
    # Also compute TF-IDF semantic similarity
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        tfidf = vectorizer.fit_transform([jd.lower(), resume_text.lower()])
        semantic_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        
        # Weighted combination: 70% keyword, 30% semantic
        final_score = (keyword_match_pct * 0.7) + (semantic_sim * 100 * 0.3)
    except:
        final_score = keyword_match_pct
    
    return {
        "score": round(final_score, 2),
        "overlap": sorted(overlap),
        "missing": sorted(missing)
    }


# -----------------------------------------------------------
# 5. UTILITY FUNCTIONS
# -----------------------------------------------------------

def extract_min_years(jd_text):
    """Extract minimum years of experience from JD"""
    matches = re.findall(r"(\d+)\+?\s+years?", jd_text.lower())
    if matches:
        return int(matches[0])
    return 0

def estimate_seniority(months):
    """Estimate seniority level based on total months"""
    if months < 24:
        return "Junior"
    elif months < 60:
        return "Mid"
    return "Senior"
