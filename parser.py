
import pytesseract
from PIL import Image
import pdf2image
import pdfplumber
import docx
import re
import spacy
import os

# Setup
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
nlp = spacy.load("en_core_web_sm")

# ---------- TEXT EXTRACTION ----------

def extract_text_from_docx(docx_path):
    text = ""
    doc = docx.Document(docx_path)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error with pdfplumber: {e}")
    return text

def extract_text_from_pdf_with_ocr(pdf_path):
    print(f"Trying OCR for PDF: {pdf_path}")
    try:
        images = pdf2image.convert_from_path(pdf_path)
        text = ""
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            print(f"OCR Page {i+1} first 200 chars: {page_text[:200]}")
            text += page_text
        return text
    except Exception as e:
        print(f"OCR failed: {e}")
        return ""

def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            print("No text found in PDF, using OCR fallback...")
            text = extract_text_from_pdf_with_ocr(file_path)
    elif file_path.lower().endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")
    return text

# ---------- PARSING LOGIC ----------

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_phone(text):
    phone_regex = re.compile(r'\+?\d[\d\s\-()]{8,}\d')
    match = phone_regex.search(text)
    return match.group() if match else None

def extract_email(text):
    email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    match = email_regex.search(text)
    return match.group() if match else None

def extract_skills(text):
    skill_keywords = ['python', 'java', 'sql', 'c++', 'excel', 'html', 'css', 'javascript', 'react', 'git', 'linux']
    text = text.lower()
    found_skills = [skill for skill in skill_keywords if skill in text]
    return list(set(found_skills))

def extract_experience(text):
    experience_keywords = ['experience', 'worked', 'intern', 'internship', 'project', 'employed', 'role']
    lines = text.split('\n')
    relevant = [line.strip() for line in lines if any(kw in line.lower() for kw in experience_keywords)]
    return relevant[:5]

def parse_resume(file_path):
    text = extract_text(file_path)
    return {
        "Name": extract_name(text),
        "Phone": extract_phone(text),
        "Email": extract_email(text),
        "Skills": extract_skills(text),
        "Experience Snippets": extract_experience(text)
    }

# ---------- MAIN TEST ----------

if __name__ == "__main__":
   file_path = 'sample_resumes/resume.pdf'
parsed = parse_resume(file_path)
for key, value in parsed.items():
      print(f"{key}: {value}\n")
