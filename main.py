from fastapi import FastAPI, File, UploadFile
import shutil
from starlette.responses import JSONResponse
from pathlib import Path
import PyPDF2
from fastapi.middleware.cors import CORSMiddleware
import spacy
from spacy.matcher import Matcher
import re
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import PyPDF2
from spacy.matcher import PhraseMatcher
from collections import OrderedDict

nlp = spacy.load("en_core_web_sm")

app = FastAPI()
origins = ["*"]
origins = [
    "https://resumebuilder-olive.vercel.app",
    "http://localhost:3000",  # for local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

categories = {
    "Profile": ["Contact"],
    "Summary": ["Profile", "Summary", "Professional Summary"],
    "Experience": ["Professional Experience", "Work Experience", "Work History", "Employment History", "Experience"],
    "Education": ["Education"],
    "Skills": ["Skills", "Expertise"],
    "Interests": ["Interests", "Hobbies"],
    "Languages": ["Languages"],
    "Achievements": ["Achievements", "Awards", "Accomplishments"],
    "Certifications": ["Certifications", "Certificates", "Courses"]
}

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for category, phrases in categories.items():
    patterns = [nlp.make_doc(phrase) for phrase in phrases]
    matcher.add(category, patterns)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text 

def is_potential_header(text, doc, start, end):
    # Extract the original header text from the doc to check its case
    original_text = doc[start:end].text
    
    # Rule out headers that are entirely in lowercase
    if original_text.islower():
        return False
    
    # Check case pattern
    if text.isupper() or text.istitle():
        return True

    # Check position - headers often start on a new line
    if start == 0 or doc[start - 1].is_space:
        return True

    # Check for lack of punctuation at the end
    if not text[-1] in [".", ",", ";", ":", "!", "?"]:
        return True

    # Check for whitespace after potential header
    if end < len(doc) and doc[end].is_space:
        return True

    # Check for length - headers are often shorter
    if len(text.split()) <= 4:
        return True

    # New heuristic: ensure there's a larger section of text that follows the potential header
    subsequent_text = doc[end:end+30].text  # We take the next 30 tokens for consideration
    if len(subsequent_text.split()) > 10:  # If there are more than 10 words, we consider it valid content following a header
        return True

    return False

def clean_text_content(content):
    # Replace whitespace longer than 2 characters with a single space
    cleaned_content = re.sub(r'\s{2,}', ' | ', content)
    return cleaned_content

from collections import OrderedDict

def extract_segments_from_text(text):
    doc = nlp(text)
    matches = matcher(doc)
    
    segments = OrderedDict((category, "") for category in categories)
    
    prev_end = 0
    current_header = None
    first_header_start = None

    for match_id, start, end in matches:
        span = doc[start:end]
        if is_potential_header(span.text, doc, start, end):
            if first_header_start is None:  # Set the position of the first header
                first_header_start = start
            
            if current_header:  # Storing the previous segment before moving on to the next
                segment_text = doc[prev_end:start].text.strip()
                cleaned_segment = clean_text_content(segment_text)
                if current_header in segments:  # Append to existing segment if it already exists
                    segments[current_header] += "\n\n" + "\n".join([line for line in cleaned_segment.splitlines() if line.strip()])
                else:
                    segments[current_header] = "\n".join([line for line in cleaned_segment.splitlines() if line.strip()])
            
            current_header = span.text
            prev_end = end

    if current_header:
        segment_text = doc[prev_end:].text.strip()
        cleaned_segment = clean_text_content(segment_text)
        if current_header in segments:  # Handle the case for the last segment
            segments[current_header] += "\n\n" + "\n".join([line for line in cleaned_segment.splitlines() if line.strip()])
        else:
            segments[current_header] = "\n".join([line for line in cleaned_segment.splitlines() if line.strip()])

    if first_header_start and first_header_start > 0:
        headerless_content = doc[0:first_header_start].text.strip()
        cleaned_headerless_content = clean_text_content(headerless_content)
        segments['Headerless Content'] = "\n".join([line for line in cleaned_headerless_content.splitlines() if line.strip()])
        segments.move_to_end('Headerless Content', last=False)

    return segments

# Define an endpoint that accepts a PDF file and converts it to text
@app.post("/convert-pdf-to-text/")
async def convert_pdf_to_text(file: UploadFile):
    # Check if the uploaded file is a PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Create a temporary directory to save the uploaded PDF
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    pdf_path = temp_dir / file.filename

    # Save the uploaded PDF to the temporary directory
    with open(pdf_path, "wb") as pdf_file:
        shutil.copyfileobj(file.file, pdf_file)

    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)

    # Extract categories (segments) from the text
    segments = extract_segments_from_text(pdf_text)

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)

    return {"pdf_text": pdf_text, "segments": segments}
