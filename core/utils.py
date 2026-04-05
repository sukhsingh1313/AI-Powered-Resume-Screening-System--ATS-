import pdfplumber
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return re.sub(r'\s+', ' ', text).strip()

def calculate_match_score(resume_text, job_description):
    if not resume_text or not job_description:
        return 0.0
    documents = [job_description.lower(), resume_text.lower()]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    match_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(match_score * 100, 2)

def extract_contact_info(resume_text):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text)
    phones = re.findall(r'\+?\d[\d\s-]{8,14}\d', resume_text)
    linkedin = re.findall(r'(https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+)', resume_text)
    return {
        'email': emails[0] if emails else "Not Found",
        'phone': phones[0] if phones else "Not Found",
        'linkedin': linkedin[0] if linkedin else "Not Found"
    }

# 👇 NAYA AI FUNCTION: Interview Questions Generator 👇
def generate_interview_questions(resume_text, required_skills):
    questions = []
    skills = [s.strip().lower() for s in required_skills.split(',')]
    text_lower = resume_text.lower()
    
    for skill in skills:
        if skill in text_lower:
            questions.append(f"🔹 You mentioned experience with '{skill.title()}'. Can you walk me through a specific project where you used it effectively?")
        else:
            questions.append(f"🔸 We didn't see '{skill.title()}' directly in your resume, but it's important for this role. How quickly can you adapt to or learn this skill?")
            
    # Sirf top 3 questions return karenge
    return "\n\n".join(questions[:3])