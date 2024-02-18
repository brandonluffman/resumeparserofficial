from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from actionwords import actionWordsList
import PyPDF2
import re
import io



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

# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         text = ''
#         for page in reader.pages:
#             text += page.extract_text() + '\n'
#     return text

def extract_text_from_pdf(pdf_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'
    return text
# Example usage
# pdf_path = '/Users/brandonluffman/resumeparserofficial/resume.pdf'
# text = extract_text_from_pdf(pdf_path)



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
        return True
    else:
        return False



# Grammar #


# Action Words #

def check_action_words_in_text(actionWordsList, text):
    matches = []

    for word in actionWordsList:
        pattern = r'\b' + word + r'\b'  # Using word boundaries to ensure whole word match
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




# print("Phone Number:", find_phone_number(text))
# print("Email Address:", find_email_address(text))
# print("Address:", find_address(text))
# category_presence = check_categories(text, categories)
# for category, present in category_presence.items():
#     print(f"{category}: {'Yes' if present else 'No'}")
# print("One Page:", is_one_page(pdf_path))
# print("First Person Pronouns:", contains_first_person_pronouns(text))


@app.post("/parse-resume/")
async def parse_resume(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    print(text)

    data = {
        "Phone Number": find_phone_number(text),
        "Email Address": find_email_address(text),
        "Address": find_address(text),
        "Categories": check_categories(text, categories),
        "Is One Page": is_one_page(contents),
        "Contains First Person Pronouns": contains_first_person_pronouns(text),
        "Has Action Words": check_action_words_in_text(actionWordsList, text)
    }
    
    return data
