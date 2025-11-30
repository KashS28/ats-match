**#** ATS Resume Matcher - Complete Project

A production-grade ATS (Applicant Tracking System) resume matcher that analyzes resume-job description compatibility with intelligent document parsing and actionable insights.

**##** Features

**-****Multi-format Support******: PDF, DOCX, JSON, TXT resume files
**-****Intelligent Parsing******: Automatic section detection and text extraction
**-****Production Algorithm******: Master prompt implementation with 72% accuracy calibration
**-****Real-time Analysis******: Upload and analyze resumes instantly
**-****Clean Interface******: Streamlit web app with intuitive design
**-****Missing Skills Analysis******: Clear gap identification without clutter

**##** Quick Start

**###** 1. Setup Project
**```**bash**
**# Clone or create project directory**
**mkdir** ats-matcher
**cd** ats-matcher
**
**# Create virtual environment**
python -m venv venv
**source** venv/bin/activate  **# Windows: venv\Scripts\activate**

**# Install dependencies**
**pip **install** -r requirements.txt**
**```**

**###** 2. Add Resume Files
**``**bash** **# Create resumes folder** **mkdir** resumes ** **# Add your resume files (any format):** **# - resume1.pdf** **# - resume2.docx  ** **# - resume3.json** **# - resume4.txt** **``**

**###** 3. Run Application
**``**bash** **streamlit run app.py** **``

Visit **`http://localhost:8501`** to use the application.

**##** Project Structure
**``** **ats-matcher/ **├── app.py                    # Main Streamlit application ├── convert_docs.py          # Standalone document converter   ├── requirements.txt         # Python dependencies ├── resumes/                 # Resume files directory │   ├── candidate_1.pdf      # PDF files (auto-converted) │   ├── candidate_2.docx     # DOCX files (auto-converted) │   ├── candidate_1.json     # Generated JSON files │   └── candidate_2.json ├── README.md               # This file **└── temp_uploads/           # Temporary upload folder (auto-created)** **``**

**##** Usage Guide

**###** Method 1: Upload & Analyze
**1.** Open the Streamlit app
**2.** Upload a PDF/DOCX file using the file uploader
**3.** Paste job description in the text area
**4.** Click "Analyze Match"
**5.** View results and missing skills

**###** Method 2: Batch Processing
**1.** Add multiple resume files to the **`resumes/`** folder
**2.** Run the app - files are automatically converted
**3.** Use the dropdown to select different resumes
**4.** Compare multiple candidates against the same JD

**###** Method 3: Command Line Conversion
**```**bash**
**# Convert single file**
**python convert_docs.py resume.pdf

**# Convert entire folder**
python convert_docs.py resumes/ -f

**# Convert with custom output**
**python convert_docs.py resume.docx -o processed_resume.json**
**```**

**##** Supported File Formats

**###** Input Formats
**-****PDF******: Text extraction via PyPDF2
**-****DOCX/DOC******: Text extraction via python-docx
**-****JSON******: Pre-structured resume data
**-****TXT******: Simple text format (sections separated by blank lines)

**###** Auto-Generated JSON Structure
**``**json** **{** **"education"**:**"Educational background..."**,** **"experience"**:**"Work experience with bullets..."**,** **"skills"**:**"Technical and soft skills..."**,** **"projects"**:**"Project descriptions and achievements..."** **}** **``**

**##** Algorithm Overview

The system uses a production-grade scoring algorithm with these components:

**-****Required Core Skills (35%)******: Programming languages, algorithms, domain expertise
**-****Responsibilities Alignment (20%)******: Semantic matching between JD and resume content
**-****Preferred Skills Match (15%)******: Nice-to-have skills with soft scoring curve
**-****Education Alignment (10%)******: Degree level and field matching
**-****Evidence Strength (10%)******: Quantified results and impact metrics
**-****Keyword Coverage (5%)******: JD phrase coverage in resume
**-****ATS Hygiene (5%)******: Resume structure and formatting

**###** Key Features
**-****Atomic token preservation******: Handles C++, Node.js correctly
**-****Synonym matching******: Cross-functional = multidisciplinary
**-****Context-aware scoring******: Project evidence > skills lists
**-****Must-have clamping******: Missing required skills caps score at 80%
**-****Impact bonuses******: Strong quantified results get +2 points

**##** Document Parsing Intelligence

**###** Section Detection
The system automatically identifies resume sections using:
**-****Header patterns******: "Education", "Experience", "Skills", "Projects"
**-****Content analysis******: Keywords like "university", "company", "python"
**-****Fallback logic******: Categorizes content when headers are unclear

**###** Text Extraction
**-****PDF handling******: Multi-page extraction with layout preservation
**-****DOCX processing******: Full document text including formatting
**-****Error handling******: Graceful failure with informative messages
**-****Auto-save******: Converted files saved as JSON for future use

**##** Deployment Options

**###** Local Development
**``**bash** **streamlit run app.py **# Access at http://localhost:8501** **``**

**###** Streamlit Cloud
**1.** Push code to GitHub repository
**2.** Visit **[**share.streamlit.io**](**https://share.streamlit.io**)**
**3.** Connect repository and deploy
**4.** Upload resume files through the web interface

**###** Docker Deployment
**```**dockerfile**
**FROM** python:3.9-slim**

**WORKDIR** /app**
**COPY** requirements.txt .**
**RUN** pip install -r requirements.txt**
**
**COPY** . .**
**EXPOSE** 8501**

**CMD** [**"streamlit"**, **"run"**, **"app.py"**, **"--server.port=8501"**, **"--server.address=0.0.0.0"**]**
**```

Build and run:
**``**bash** **docker** build -t ats-matcher **.** **docker** run -p **8501**:8501 ats-matcher** **``**

**##** Customization

**###** Adding New Skills
Edit the **`build_ontology()`** function in **`app.py`**:
**``**python** **"New Skill Category"**:**{** **"terms"**:**[**"skill1"**,**"skill2"**,**"skill3"**]**,** **"synonyms"**:**{**"skill1"**:**[**"synonym1"**,**"synonym2"**]**}**,** **"weight"**:**0.15**,** **"type"**:**"required"**# or "preferred"** **}** **``

**###** Adjusting Score Weights
Modify the **`weights`** dictionary in **`score_resume_to_jd()`**:
**``**python** **weights **=**{** **'RCS'**:**40**,**# Increase required skills importance** **'RRA'**:**15**,**# Decrease responsibilities alignment** **'PSM'**:**15**,**'EDU'**:**10**,**'EES'**:**10**,**'KC'**:**5**,**'ATS'**:**5** **}** **``

**###** Custom Document Parsing
Enhance **`parse_resume_text_to_sections()`** for:
**-** Domain-specific section names
**-** Multi-language support
**-** Advanced NLP processing
**-** Custom regex patterns

**##** Troubleshooting

**###** Common Issues

******PDF Extraction Problems******
**-** Scanned PDFs: Need OCR preprocessing
**-** Complex layouts: May scramble text order
**-** Password protected: Not supported

******DOCX Processing Issues******
**-** Old .doc files: Limited support, convert to .docx
**-** Embedded objects: Tables and images ignored
**-** Corrupted files: Error messages displayed

******Low Scores******
**-** Technical terms missing: Algorithm calibrated for tech roles
**-** Generic descriptions: Add specific technologies and metrics
**-** Section misclassification: Check manual JSON format

******File Upload Errors******
**-** Large files: May timeout, try smaller files or local processing
**-** Network issues: Use folder method instead of upload
**-** Encoding problems: Ensure UTF-8 file encoding

**###** Solutions

**1.****Use JSON format****** for complex resumes that don't parse well
**2.****Clean up PDFs****** by converting through Google Docs first
**3.****Add quantified results****** with percentages and numbers
**4.****Check file encoding****** if special characters appear garbled
**5.****Use local processing****** for batch operations or large files

**##** Performance Notes

**-****Processing time******: 1-3 seconds per document depending on size
**-****Memory usage******: ~100MB for typical resume processing
**-****Concurrent users******: Streamlit handles multiple users efficiently
**-****File size limits******: Recommended max 10MB per document

**##** Contributing

To contribute to this project:
**1.** Fork the repository
**2.** Create feature branch: **`git checkout -b new-feature`**
**3.** Make changes and test thoroughly
**4.** Submit pull request with clear description

**###** Development Setup
**```**bash**
**# Install development dependencies**
**pip **install** -r requirements.txt
**pip **install** pytest black flake8
**
**# Run tests**
python -m pytest

**# Format code**
black app.py convert_docs.py

**# Check style**
**flake8 app.py convert_docs.py**
**```**

**##** License

This project is open source. Feel free to use, modify, and distribute according to your needs.

**##** Support

For questions or issues:
**1.** Check the troubleshooting section above
**2.** Review error messages for specific guidance
**3.** Ensure all dependencies are installed correctly
**4.** Try different file formats if parsing fails

**---**

******Happy matching!****** This tool should help streamline your resume screening process with accurate, explainable results.
