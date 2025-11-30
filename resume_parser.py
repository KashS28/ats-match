import re
from typing import Dict, Any, List
from dateutil import parser as dateparser
import datetime
from utils import clean_text

DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})[\w\.\- ]*\d{2,4})"
    r"\s*(?:–|-|to)\s*"
    r"(?P<end>(?:Present|Now|Current|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})[\w\.\- ]*\d{2,4})",
    re.IGNORECASE,
)

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


def parse_date_token(token: str):
    token = token.strip()
    try:
        return dateparser.parse(token, default=datetime.datetime(2000, 1, 1)).date()
    except:
        return None


def months_between(start, end):
    if not start or not end:
        return None
    return (end.year - start.year) * 12 + (end.month - start.month)


# ---------------------------
# EXPERIENCE PARSING
# ---------------------------

def extract_experience_blocks(text: str) -> List[str]:
    blocks = []
    lines = [ln.rstrip() for ln in text.splitlines()]

    current = []
    for ln in lines:
        if DATE_RANGE_PATTERN.search(ln):
            if current:
                blocks.append("\n".join(current))
                current = []
        current.append(ln)

    if current:
        blocks.append("\n".join(current))
    return blocks


def parse_experience_block(block: str) -> Dict[str, Any]:
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    if not lines:
        return {}

    # 1) Date line
    date_line_index = None
    date_match = None

    for i, ln in enumerate(lines):
        m = DATE_RANGE_PATTERN.search(ln)
        if m:
            date_line_index = i
            date_match = m
            break

    start_dt = end_dt = None
    months = None
    date_text = ""

    if date_match:
        sTok, eTok = date_match.group("start"), date_match.group("end")
        start_dt = parse_date_token(sTok)
        end_dt = parse_date_token(eTok)
        if start_dt and end_dt:
            months = months_between(start_dt, end_dt)
            date_text = date_match.group(0)

    # 2) Split header/body
    if date_line_index is not None:
        header_lines = lines[:date_line_index]
        body_lines = lines[date_line_index + 1 :]
    else:
        header_lines = lines[:2]
        body_lines = lines[2:]

    # Guess title + company
    title = header_lines[0] if header_lines else ""
    company = header_lines[1] if len(header_lines) > 1 else ""

    # Bullets
    bullets = []
    for ln in body_lines:
        if ln.lstrip().startswith(("•", "-", "*")):
            bullets.append(ln.lstrip("•-* "))
        else:
            bullets.append(ln)

    return {
        "title": title,
        "company": company,
        "location": "",
        "date_text": date_text,
        "start_date": start_dt.isoformat() if start_dt else None,
        "end_date": end_dt.isoformat() if end_dt else None,
        "months": months or 0,
        "employment_type": "FT",
        "bullets": bullets,
    }


# ---------------------------
# EDUCATION
# ---------------------------

def extract_education(text: str) -> List[Dict[str, Any]]:
    lines = text.splitlines()
    entries = []
    block = []

    for ln in lines:
        if "university" in ln.lower() or "institute" in ln.lower():
            if block:
                entries.append("\n".join(block))
                block = []
        block.append(ln)

    if block:
        entries.append("\n".join(block))

    parsed = []
    for blk in entries:
        ls = [l.strip() for l in blk.splitlines() if l.strip()]
        inst = ls[0] if ls else ""
        degree = ls[1] if len(ls) > 1 else ""
        parsed.append({
            "institution": inst,
            "degree": degree,
            "location": "",
            "graduation": "",
            "courses": ""
        })
    return parsed


# ---------------------------
# PROJECTS
# ---------------------------

def extract_projects(text: str) -> List[Dict[str, Any]]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    projects = []
    block = []

    for ln in lines:
        if not ln.startswith(("•", "-", "*")) and ln[0].isupper():
            if block:
                projects.append("\n".join(block))
                block = []
        block.append(ln)

    if block:
        projects.append("\n".join(block))

    final = []
    for blk in projects:
        ls = [x for x in blk.splitlines() if x.strip()]
        title = ls[0]
        bullets = []
        for t in ls[1:]:
            bullets.append(t.lstrip("•-* "))

        final.append({"title": title, "bullets": bullets})
    return final


# ---------------------------
# MAIN PARSER
# ---------------------------

def parse_resume_text(text: str) -> Dict[str, Any]:
    exp_blocks = extract_experience_blocks(text)
    experiences = [parse_experience_block(b) for b in exp_blocks]

    edus = extract_education(text)
    projs = extract_projects(text)

    skills = []
    if "skills" in text.lower():
        skill_block = text.lower().split("skills")[1]
        skills = [s.strip() for s in re.split("[,;\n]", skill_block) if len(s.strip()) > 2]

    return {
        "experience": experiences,
        "education": edus,
        "projects": projs,
        "skills": skills
    }