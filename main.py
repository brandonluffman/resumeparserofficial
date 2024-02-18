from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from actionwords import actionWordsList
import PyPDF2
import re
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter



app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


categories = {
    "Experience": ["Professional Experience", "Work Experience", "Work History", "Employment History", "Experience"],
    "Education": ["Education"],
    "Skills": ["Skills"]
}


#### Resume Text Extraction ######
def extract_text_from_pdf(pdf_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'
    return text



#### Sections ####

# Phone Number #
def find_phone_number(text):
    phone_pattern = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
    match = phone_pattern.search(text)
    return match.group() if match else None

# Email Address #
def find_email_address(text):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    match = email_pattern.search(text)
    return match.group() if match else None


# Address #
def find_address(text):
    # List of US state abbreviations for the regex pattern
    states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
              'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
              'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
              'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
              'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
    pattern = r'\b([A-Za-z]+(?: [A-Za-z]+)*),? (' + '|'.join(states) + r')\b'
    match = re.search(pattern, text)
    return match.group() if match else None

# Categories #
def check_categories(text, categories):
    category_presence = {}
    for category, keywords in categories.items():
        pattern = re.compile('|'.join([re.escape(keyword) for keyword in keywords]), re.IGNORECASE)
        category_presence[category] = bool(pattern.search(text))
    return category_presence



#### Rules ####
    
# One Page #
def is_one_page(pdf_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    return len(reader.pages) == 1


# First Person Pronouns #
def contains_first_person_pronouns(text):
    # Define a list of first person pronouns
    pronouns = ["I", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"]

    # Use regex to match words to ensure that substrings inside other words aren't counted
    matches = []

    for pronoun in pronouns:
        pattern = r'\b' + pronoun + r'\b'  # Using word boundaries to ensure whole word match
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pronoun)
    
    print(matches)

    if len(matches) > 0:
        return False
    else:
        return True



# Grammar #


# Action Words #
def check_action_words_in_text(actionWordsList, text):
    matches = []

    for word in actionWordsList:
        pattern = r'\b' + word + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(word)

    if len(matches) > 0:
        print(matches)
        matches = True;
        print('There are matches')
    else:
        matches = False;
        print('There are no matches')
    return matches

# Quantify 
def check_quantify(text):
    pattern = r'(\d+(\.\d{1,2})?)%'
    matches = re.findall(pattern, text)    
    percentages = [match[0] for match in matches]
    if percentages:
        percentages = True;
    else:
        percentages = False;
    
    return percentages



# print("Phone Number:", find_phone_number(text))
# print("Email Address:", find_email_address(text))
# print("Address:", find_address(text))
# category_presence = check_categories(text, categories)
# for category, present in category_presence.items():
#     print(f"{category}: {'Yes' if present else 'No'}")
# print("One Page:", is_one_page(pdf_path))
# print("First Person Pronouns:", contains_first_person_pronouns(text))
# pdf_path = '/Users/brandonluffman/resumeparserofficial/resume.pdf'
# text = extract_text_from_pdf(pdf_path)


@app.post("/parse-resume/")
async def parse_resume(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_pdf(contents)

    data = {
        "Phone Number": find_phone_number(text),
        "Email Address": find_email_address(text),
        "Address": find_address(text),
        "Categories": check_categories(text, categories),
        "Is One Page": is_one_page(contents),
        "Contains First Person Pronouns": contains_first_person_pronouns(text),
        "Has Action Words": check_action_words_in_text(actionWordsList, text),
        "Is Quantified": check_quantify(text)
    }

    true_count = sum(value == True for value in data.values() if isinstance(value, bool))
    category_true_count = sum(data["Categories"].values())
    total_checks = len([value for value in data.values() if isinstance(value, bool)]) + len(data["Categories"])
    grade = (true_count + category_true_count) / total_checks

    data["Resume Grade"] = grade
    
    return data



@app.post("/analyze-tfidf/")
async def analyze_tfidf(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_pdf(contents)

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Convert the text into a list for the TfidfVectorizer
    text_list = [text]

    # Initialize the TfidfVectorizer with English stopwords
    vectorizer = TfidfVectorizer(stop_words='english')

    # Fit and transform the text data
    tfidf_matrix = vectorizer.fit_transform(text_list)

    # Get the feature names (words) and their TF-IDF scores
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().flatten()

    # Combine the words and their scores into a dictionary
    tfidf_dict = dict(zip(feature_names, tfidf_scores))

    # Sort the dictionary by TF-IDF scores in descending order
    sorted_tfidf_dict = dict(sorted(tfidf_dict.items(), key=lambda item: item[1], reverse=True))

    return sorted_tfidf_dict

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    return text

@app.post("/analyze-texts/")
async def analyze_texts(job_description: str = Form(...), resume: UploadFile = File(...)):
    # Extract text from resume PDF
    resume_contents = await resume.read()
    resume_text = extract_text_from_pdf(resume_contents)

    # Preprocess job description and resume text
    job_description = preprocess_text(job_description)
    resume_text = preprocess_text(resume_text)

    # Analyze job description text using TF-IDF
    job_vectorizer = TfidfVectorizer(stop_words='english')
    job_tfidf_matrix = job_vectorizer.fit_transform([job_description])
    job_feature_names = job_vectorizer.get_feature_names_out()
    job_tfidf_scores = job_tfidf_matrix.toarray().flatten()
    job_tfidf_dict = dict(zip(job_feature_names, job_tfidf_scores))
    sorted_job_tfidf_dict = dict(sorted(job_tfidf_dict.items(), key=lambda item: item[1], reverse=True))

    # Analyze resume text using TF-IDF
    resume_vectorizer = TfidfVectorizer(stop_words='english')
    resume_tfidf_matrix = resume_vectorizer.fit_transform([resume_text])
    resume_feature_names = resume_vectorizer.get_feature_names_out()
    resume_tfidf_scores = resume_tfidf_matrix.toarray().flatten()
    resume_tfidf_dict = dict(zip(resume_feature_names, resume_tfidf_scores))
    sorted_resume_tfidf_dict = dict(sorted(resume_tfidf_dict.items(), key=lambda item: item[1], reverse=True))

    return {
        "job_description_tfidf": sorted_job_tfidf_dict,
        "resume_tfidf": sorted_resume_tfidf_dict
    }