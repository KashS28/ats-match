# streamlit_app.py - UPDATED WITH WEIGHTED CALCULATION
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
st.header("Step 1: Upload Resume")
resume_file = st.file_uploader("Upload PDF, DOCX or TXT", type=["pdf", "docx", "txt"])

if resume_file:
    raw_text = load_resume_text(resume_file)
    parsed = parse_resume_to_json(raw_text)
    st.session_state["parsed_resume"] = parsed
    st.session_state["resume_text"] = raw_text
    st.success("✅ Resume parsed. Review and edit below.")

# Require parsed resume to proceed
if "parsed_resume" not in st.session_state:
    st.info("📤 Upload a resume to begin parsing and editing.")
    st.stop()

parsed = st.session_state["parsed_resume"]

# ---------- Experience ----------
st.header("📋 Experience")
exp_list: List[dict] = parsed.get("experience", [])
edited_exps = []

for i, exp in enumerate(exp_list):
    st.markdown(f"### Role {i+1}")
    
    cols = st.columns([3, 3])
    company = cols[0].text_input(
        f"Company {i+1}", 
        value=exp.get("company", ""), 
        key=f"company_{i}",
        help="Company or organization name"
    )
    role = cols[1].text_input(
        f"Role {i+1}", 
        value=exp.get("title", ""), 
        key=f"role_{i}",
        help="Job title or role"
    )
    
    cols2 = st.columns([2, 2, 2, 2])
    start = cols2[0].text_input(
        f"From {i+1}", 
        value=(exp.get("start_date") or ""), 
        key=f"start_{i}",
        help="Format: YYYY-MM (e.g., 2024-05)"
    )
    end = cols2[1].text_input(
        f"To {i+1}", 
        value=(exp.get("end_date") or ""), 
        key=f"end_{i}",
        help="Format: YYYY-MM or 'Present'"
    )
    
    # Show months (read-only)
    months = exp.get("months", 0)
    cols2[2].text_input(
        f"Months {i+1}", 
        value=str(months), 
        key=f"months_{i}", 
        disabled=True,
        help="Auto-calculated from dates"
    )
    
    emp_type = cols2[3].selectbox(
        f"Type {i+1}", 
        options=["FT", "PT", "INT"], 
        index=["FT", "PT", "INT"].index(exp.get("employment_type", "FT")), 
        key=f"etype_{i}",
        help="FT=Full-time, PT=Part-time, INT=Internship"
    )
    
    bullets_text = "\n".join(exp.get("bullets", []))
    bullets_edit = st.text_area(
        f"Bullets {i+1} (one per line)", 
        value=bullets_text, 
        height=120, 
        key=f"bullets_{i}",
        help="Add one bullet point per line"
    )
    bullets = [b.strip() for b in bullets_edit.splitlines() if b.strip()]

    edited_exps.append({
        "company": company.strip(),
        "title": role.strip(),
        "start_date": start.strip() or None,
        "end_date": end.strip() or None,
        "months": months,
        "employment_type": emp_type,
        "bullets": bullets,
    })
    
    st.markdown("---")

# ---------- Education ----------
st.header("🎓 Education")
edu_list: List[dict] = parsed.get("education", [])
edited_edus = []

for i, edu in enumerate(edu_list):
    st.markdown(f"### Education {i+1}")
    
    cols = st.columns([5, 5, 2])
    inst = cols[0].text_input(
        f"Institution {i+1}", 
        value=edu.get("institution", ""), 
        key=f"inst_{i}"
    )
    degree = cols[1].text_input(
        f"Degree {i+1}", 
        value=edu.get("degree", ""), 
        key=f"deg_{i}"
    )
    grad = cols[2].text_input(
        f"Year {i+1}", 
        value=(edu.get("graduation_date") or ""), 
        key=f"grad_{i}",
        help="Graduation year"
    )
    
    cols2 = st.columns([6, 6])
    gpa = cols2[0].text_input(
        f"GPA {i+1}", 
        value=str(edu.get("gpa") or ""), 
        key=f"gpa_{i}",
        help="e.g., 3.8"
    )
    
    courses_text = ", ".join(edu.get("courses", []))
    courses_edit = cols2[1].text_input(
        f"Courses {i+1}", 
        value=courses_text, 
        key=f"courses_{i}",
        help="Comma-separated course names"
    )
    courses = [c.strip() for c in courses_edit.split(",") if c.strip()]

    edited_edus.append({
        "institution": inst.strip(),
        "degree": degree.strip(),
        "graduation_date": grad.strip() or None,
        "gpa": float(gpa) if gpa.strip() else None,
        "courses": courses,
    })
    
    st.markdown("---")

# ---------- Projects ----------
st.header("🚀 Projects")
proj_list: List[dict] = parsed.get("projects", [])
edited_projects = []

for i, proj in enumerate(proj_list):
    st.markdown(f"### Project {i+1}")
    
    title = st.text_input(
        f"Project Title {i+1}", 
        value=proj.get("title", ""), 
        key=f"proj_title_{i}"
    )
    
    bullets_text = "\n".join(proj.get("bullets", []))
    bullets_edit = st.text_area(
        f"Project Bullets {i+1} (one per line)", 
        value=bullets_text, 
        height=120, 
        key=f"proj_bullets_{i}"
    )
    bullets = [b.strip() for b in bullets_edit.splitlines() if b.strip()]
    
    edited_projects.append({
        "title": title.strip(), 
        "bullets": bullets
    })
    
    st.markdown("---")

# ---------- Skills ----------
st.header("🛠️ Skills")
skills_flat = parsed.get("skills", {}).get("all", []) if isinstance(parsed.get("skills"), dict) else parsed.get("skills", [])
skills_str = ", ".join(skills_flat)
skills_edit = st.text_area(
    "Skills (comma-separated)", 
    value=skills_str, 
    key="skills_edit",
    height=100,
    help="List all your technical skills, separated by commas"
)
edited_skills = [s.strip() for s in skills_edit.split(",") if s.strip()]

# ---------- Save Parsed Resume ----------
st.markdown("---")
if st.button("💾 Save Parsed Resume", type="primary", use_container_width=True):
    new_parsed = {
        "experience": edited_exps,
        "education": edited_edus,
        "projects": edited_projects,
        "skills": {"all": edited_skills},
    }
    st.session_state["parsed_resume"] = new_parsed

    # ========================================
    # WEIGHTED MONTHS CALCULATION
    # ========================================
    # Formula: FT * 1.0 + PT * 0.6 + INT * 0.8
    
    total_weighted = 0.0
    ft_months = 0
    pt_months = 0
    int_months = 0
    
    for e in edited_exps:
        months = e.get("months") or 0
        emp_type = e.get("employment_type", "FT")
        
        if emp_type == "FT":
            ft_months += months
            weight = 1.0
        elif emp_type == "INT":
            int_months += months
            weight = 0.8
        else:  # PT
            pt_months += months
            weight = 0.6
        
        total_weighted += months * weight
    
    st.session_state["weighted_months"] = total_weighted
    st.session_state["ft_months"] = ft_months
    st.session_state["pt_months"] = pt_months
    st.session_state["int_months"] = int_months
    
    # Show breakdown
    st.success(f"✅ Resume saved!")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("FT Months", f"{ft_months}")
    with col2:
        st.metric("PT Months", f"{pt_months}")
    with col3:
        st.metric("INT Months", f"{int_months}")
    with col4:
        st.metric("Weighted Total", f"{round(total_weighted, 1)}")
    
    # Show calculation
    with st.expander("📊 Weighted Calculation Details"):
        st.markdown(f"""
        **Formula:** `(FT × 1.0) + (PT × 0.6) + (INT × 0.8)`
        
        **Your Calculation:**
        - Full-time: {ft_months} months × 1.0 = {ft_months}
        - Part-time: {pt_months} months × 0.6 = {pt_months * 0.6}
        - Internship: {int_months} months × 0.8 = {int_months * 0.8}
        
        **Total Weighted:** {round(total_weighted, 1)} months ({round(total_weighted/12, 1)} years)
        """)
    
    # Show JSON snapshot
    with st.expander("📄 View Resume JSON"):
        st.json(new_parsed)

# ---------- JD Analysis ----------
st.markdown("---")
st.header("📋 Step 2: Job Description Analysis")

jd_text = st.text_area(
    "Paste Job Description Here:", 
    height=300, 
    key="jd_text",
    placeholder="Paste the full job description including requirements, responsibilities, and qualifications..."
)

if st.button("🚀 Analyze Match", type="primary", use_container_width=True):
    if "parsed_resume" not in st.session_state:
        st.error("❌ Please save your parsed resume first!")
        st.stop()
    
    if not jd_text.strip():
        st.error("❌ Please paste a job description!")
        st.stop()

    parsed_resume = st.session_state["parsed_resume"]
    resume_text = st.session_state.get("resume_text", "")
    
    # Compute skill match
    match_details = compute_skill_match(jd_text, resume_text)
    skills_pct = match_details["score"]
    
    # Extract JD requirements
    min_years = extract_min_years(jd_text)
    min_months_required = min_years * 12
    
    # Get weighted months
    weighted_months = st.session_state.get("weighted_months", 0)
    
    st.markdown("---")
    st.subheader("📊 Results")
    
    # Overall summary cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score_color = "🟢" if skills_pct >= 75 else "🟡" if skills_pct >= 60 else "🔴"
        st.metric(
            "Skills Match",
            f"{score_color} {skills_pct}%",
            help="Percentage of JD skills found in your resume"
        )
    
    with col2:
        exp_status = "✅" if weighted_months >= min_months_required else "❌"
        st.metric(
            "Experience",
            f"{exp_status} {round(weighted_months/12, 1)} years",
            f"Required: {min_years} years",
            help="Weighted experience (FT×1.0 + PT×0.6 + INT×0.8)"
        )
    
    with col3:
        overall_pass = skills_pct >= 75 and weighted_months >= min_months_required
        st.metric(
            "Overall",
            "✅ PASS" if overall_pass else "❌ FAIL",
            help="Both skills and experience must pass"
        )
    
    st.markdown("---")
    
    # Detailed gates
    st.subheader("🚦 Gate Analysis")
    
    # Experience Gate
    if weighted_months >= min_months_required:
        st.success(f"✅ **Experience Gate: PASS**")
        st.caption(f"You have {round(weighted_months, 1)} weighted months ({round(weighted_months/12, 1)} years) | Required: {min_months_required} months ({min_years} years)")
    else:
        st.error(f"❌ **Experience Gate: FAIL**")
        st.caption(f"You have {round(weighted_months, 1)} weighted months ({round(weighted_months/12, 1)} years) | Required: {min_months_required} months ({min_years} years)")
        shortage = min_months_required - weighted_months
        st.warning(f"⚠️ You need {round(shortage, 1)} more weighted months ({round(shortage/12, 1)} years)")
    
    # Skills Gate
    MATCH_THRESHOLD = 75.0
    if skills_pct >= MATCH_THRESHOLD:
        st.success(f"✅ **Skills Gate: PASS**")
        st.caption(f"Your match: {skills_pct}% | Threshold: {MATCH_THRESHOLD}%")
    else:
        st.error(f"❌ **Skills Gate: FAIL**")
        st.caption(f"Your match: {skills_pct}% | Threshold: {MATCH_THRESHOLD}%")
        gap = MATCH_THRESHOLD - skills_pct
        st.warning(f"⚠️ You need {round(gap, 1)}% more skill coverage")
    
    st.markdown("---")
    
    # Skills breakdown
    st.subheader("🎯 Skills Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Matched Skills")
        if match_details.get("overlap"):
            matched = match_details["overlap"]
            st.success(f"**{len(matched)} skills matched**")
            # Show in a nice format
            matched_text = ", ".join(matched)
            st.text_area("", matched_text, height=200, key="matched", disabled=True)
        else:
            st.info("No matched skills found")
    
    with col2:
        st.markdown("### ❌ Missing Skills")
        if match_details.get("missing"):
            missing = match_details["missing"]
            st.error(f"**{len(missing)} skills missing**")
            # Show in a nice format
            missing_text = ", ".join(missing)
            st.text_area("", missing_text, height=200, key="missing", disabled=True)
        else:
            st.success("No missing skills!")
    
    st.markdown("---")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    if not overall_pass:
        st.markdown("**To improve your application:**")
        
        recommendations = []
        
        if weighted_months < min_months_required:
            recommendations.append(
                f"🔹 **Gain more experience:** You need {round((min_months_required - weighted_months)/12, 1)} more years of weighted experience"
            )
        
        if skills_pct < MATCH_THRESHOLD:
            top_missing = match_details["missing"][:5]
            recommendations.append(
                f"🔹 **Learn these skills:** {', '.join(top_missing)}"
            )
            recommendations.append(
                "🔹 **Add keywords to resume:** Include exact terms from the JD in your skills and experience sections"
            )
        
        for rec in recommendations:
            st.markdown(rec)
    else:
        st.success("🎉 **You're a strong candidate! Apply with confidence.**")
        st.balloons()
