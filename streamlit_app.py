# streamlit_app.py
import streamlit as st
import json
from typing import List

from app import (
    load_resume_text,
    parse_resume_to_json,
    compute_skill_match,
    extract_min_years,
    estimate_seniority,
)

st.set_page_config(page_title="ATS Resume Matcher", layout="centered")
st.title("ATS Resume Matcher")

# ---------- Upload ----------
st.header("Step 1 Upload resume")
resume_file = st.file_uploader("Upload PDF DOCX or TXT", type=["pdf", "docx", "txt"])

if resume_file:
    raw_text = load_resume_text(resume_file)
    parsed = parse_resume_to_json(raw_text)
    st.session_state["parsed_resume"] = parsed
    st.session_state["resume_text"] = raw_text
    st.success("Resume parsed. Review and edit below.")

# require parsed resume to proceed
if "parsed_resume" not in st.session_state:
    st.info("Upload a resume to parse and edit fields.")
    st.stop()

parsed = st.session_state["parsed_resume"]

# ---------- Experience ----------
st.header("Experience")
exp_list: List[dict] = parsed.get("experience", [])
edited_exps = []

for i, exp in enumerate(exp_list):
    st.markdown(f"**Role {i+1}**")
    cols = st.columns([3, 3, 2, 2])
    company = cols[0].text_input(f"Company {i+1}", value=exp.get("company", ""), key=f"company_{i}")
    role = cols[1].text_input(f"Role {i+1}", value=exp.get("title", ""), key=f"role_{i}")
    start = cols[2].text_input(f"From {i+1} (YYYY-MM or text)", value=(exp.get("start_date") or ""), key=f"start_{i}")
    end = cols[3].text_input(f"To {i+1} (YYYY-MM or Present)", value=(exp.get("end_date") or ""), key=f"end_{i}")
    months = exp.get("months", "")
    st.text_input(f"Months computed {i+1}", value=str(months), key=f"months_{i}", disabled=True)
    emp_type = st.selectbox(f"Employment type {i+1}", options=["FT", "PT", "INT"], index=["FT", "PT", "INT"].index(exp.get("employment_type", "FT")), key=f"etype_{i}")
    bullets_text = "\n".join(exp.get("bullets", []))
    bullets_edit = st.text_area(f"Bullets {i+1} (one per line)", value=bullets_text, height=120, key=f"bullets_{i}")
    bullets = [b.strip() for b in bullets_edit.splitlines() if b.strip()]

    edited_exps.append(
        {
            "company": company.strip(),
            "title": role.strip(),
            "start_date": start.strip() or None,
            "end_date": end.strip() or None,
            "months": months,
            "employment_type": emp_type,
            "bullets": bullets,
        }
    )
    st.markdown("---")

# ---------- Education ----------
st.header("Education")
edu_list: List[dict] = parsed.get("education", [])
edited_edus = []

for i, edu in enumerate(edu_list):
    st.markdown(f"**Education {i+1}**")
    cols = st.columns([4, 4, 2])
    inst = cols[0].text_input(f"College / Institution {i+1}", value=edu.get("institution", ""), key=f"inst_{i}")
    degree = cols[1].text_input(f"Degree {i+1}", value=edu.get("degree", ""), key=f"deg_{i}")
    grad = cols[2].text_input(f"Graduation {i+1} (YYYY or text)", value=(edu.get("graduation_date") or ""), key=f"grad_{i}")
    gpa = st.text_input(f"GPA {i+1}", value=str(edu.get("gpa") or ""), key=f"gpa_{i}")
    courses_text = ", ".join(edu.get("courses", []))
    courses_edit = st.text_input(f"Courses {i+1} (comma separated)", value=courses_text, key=f"courses_{i}")
    courses = [c.strip() for c in courses_edit.split(",") if c.strip()]

    edited_edus.append(
        {
            "institution": inst.strip(),
            "degree": degree.strip(),
            "graduation_date": grad.strip() or None,
            "gpa": float(gpa) if gpa.strip() else None,
            "courses": courses,
        }
    )
    st.markdown("---")

# ---------- Projects ----------
st.header("Projects")
proj_list: List[dict] = parsed.get("projects", [])
edited_projects = []

for i, proj in enumerate(proj_list):
    st.markdown(f"**Project {i+1}**")
    title = st.text_input(f"Project name {i+1}", value=proj.get("title", ""), key=f"proj_title_{i}")
    bullets_text = "\n".join(proj.get("bullets", []))
    bullets_edit = st.text_area(f"Project bullets {i+1} (one per line)", value=bullets_text, height=120, key=f"proj_bullets_{i}")
    bullets = [b.strip() for b in bullets_edit.splitlines() if b.strip()]
    edited_projects.append({"title": title.strip(), "bullets": bullets})
    st.markdown("---")

# ---------- Skills ----------
st.header("Skills")
skills_flat = parsed.get("skills", {}).get("all", []) if isinstance(parsed.get("skills"), dict) else parsed.get("skills", [])
skills_str = ", ".join(skills_flat)
skills_edit = st.text_input("Skills (comma separated)", value=skills_str, key="skills_edit")
edited_skills = [s.strip() for s in skills_edit.split(",") if s.strip()]

# ---------- Save parsed resume ----------
if st.button("Save parsed resume"):
    new_parsed = {
        "experience": edited_exps,
        "education": edited_edus,
        "projects": edited_projects,
        "skills": {"all": edited_skills},
    }
    st.session_state["parsed_resume"] = new_parsed

    # compute weighted months for convenience
    total_weighted = 0.0
    for e in edited_exps:
        m = e.get("months") or 0
        t = e.get("employment_type", "FT")
        if t == "FT":
            w = 1.0
        elif t == "INT":
            w = 0.8
        else:
            w = 0.6
        total_weighted += m * w
    st.session_state["weighted_months"] = total_weighted
    st.success(f"Saved parsed resume. weighted months {round(total_weighted,1)}")

    # show JSON snapshot
    st.subheader("Parsed resume JSON")
    st.json(new_parsed)

# ---------- Paste JD and Analyze ----------
st.header("Step 2 Paste job description")
jd_text = st.text_area("Job Description", height=260, key="jd_text")

if st.button("Analyze"):
    if "parsed_resume" not in st.session_state:
        st.error("save parsed resume first")
        st.stop()

    parsed_resume = st.session_state["parsed_resume"]
    resume_text = st.session_state.get("resume_text", "")
    match_details = compute_skill_match(jd_text, resume_text)
    skills_pct = match_details["score"]
    min_years = extract_min_years(jd_text)
    min_months_required = min_years * 12
    weighted_months = st.session_state.get("weighted_months", 0)

    st.subheader("Results")
    st.write(f"Skills match {skills_pct}%")
    st.write(f"Weighted experience {round(weighted_months,1)} months")
    st.write(f"JD required experience {min_years} years ({min_months_required} months)")

    if weighted_months >= min_months_required:
        st.success("Experience gate eligible")
    else:
        st.error("Experience gate not eligible")

    MATCH_THRESHOLD = 75.0
    st.write(f"Skills threshold for application {MATCH_THRESHOLD}%")
    if skills_pct >= MATCH_THRESHOLD:
        st.success("Skills gate passed")
    else:
        st.error("Skills gate failed")

    st.markdown("### Explanation")
    st.write("Matched skills")
    st.write(", ".join(match_details.get("overlap", [])) or "None")
    st.write("Missing skills")
    st.write(", ".join(match_details.get("missing", [])) or "None")