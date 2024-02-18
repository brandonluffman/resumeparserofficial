import re
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException
import spacy
from spacy.matcher import Matcher
from pdfminer.high_level import extract_text
from fastapi.middleware.cors import CORSMiddleware
from spacy.matcher import PhraseMatcher
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTTextLine
from actionwords import actionWordsList
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
# import language_tool_python  
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextContainer
from pdfminer.layout import LTChar


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
nlp = spacy.load("en_core_web_sm")

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



def is_potential_header(text, doc, start, end):
    original_text = doc[start:end].text
    if original_text.islower():
        return False
    if text.isupper() or text.istitle():
        return True
    if start == 0 or doc[start - 1].is_space:
        return True
    if not text[-1] in [".", ",", ";", ":", "!", "?"]:
        return True
    if end < len(doc) and doc[end].is_space:
        return True
    if len(text.split()) <= 4:
        return True
    subsequent_text = doc[end:end+30].text
    if len(subsequent_text.split()) > 10:
        return True
    return False

def clean_text_content(content):
    return re.sub(r'\s{2,}', ' | ', content)

def extract_segments_from_text(text):
    doc = nlp(text)
    matches = matcher(doc)
    
    segments = {}
    
    prev_end = 0
    current_header = None
    first_header_start = None

    for match_id, start, end in matches:
        span = doc[start:end]
        if is_potential_header(span.text, doc, start, end):
            if first_header_start is None:
                first_header_start = start
            if current_header:
                segment_text = doc[prev_end:start].text.strip()
                cleaned_segment = clean_text_content(segment_text)
                segments[current_header] = cleaned_segment
            current_header = span.text
            prev_end = end

    if current_header:
        segment_text = doc[prev_end:].text.strip()
        cleaned_segment = clean_text_content(segment_text)
        segments[current_header] = cleaned_segment

    if first_header_start and first_header_start > 0:
        headerless_content = doc[0:first_header_start].text.strip()
        cleaned_headerless_content = clean_text_content(headerless_content)
        segments['Headerless Content'] = cleaned_headerless_content

    return segments

def extract_text_with_pdfminer(pdf_path):
    return extract_text(pdf_path)

def is_continuation_of_previous(prev_text, current_text):
    if not prev_text or not current_text:
        return False

    # Check if the previous text ends with a bullet point
    bullet_point_condition = prev_text[-1] in {'•', '-', '*', '>', '+'}

    # Check if the previous text does not end with typical sentence-ending punctuation
    end_condition = not prev_text[-1] in {'.', '!', '?'}

    # Check if the current text starts with a lowercase letter
    continuation_condition = current_text[0].islower()

    return (end_condition and continuation_condition) or bullet_point_condition

def analyze_layout(pdf_path):
    previous_text = None
    extracted_content = []

    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBox):
                for text_line in element:
                    if isinstance(text_line, LTTextLine):
                        current_text = text_line.get_text().strip()

                        if is_continuation_of_previous(previous_text, current_text):
                            previous_text += ' ' + current_text
                        else:
                            if previous_text:
                                extracted_content.append(previous_text)
                            previous_text = current_text

    # Append the last line
    if previous_text:
        extracted_content.append(previous_text)

    return '\n'.join(extracted_content)

def grade_resume(resume_text):
    doc = nlp(resume_text)
    matches = matcher(doc)
    
    detected_categories = set()  # Using a set to ensure unique categories
    education_index, experience_index = -1, -1  # Initial indices
    
    for match_id, start, end in matches:
        category_name = nlp.vocab.strings[match_id]
        detected_categories.add(category_name)

        # Update the indices when matched
        if category_name == "Education":
            education_index = start
        elif category_name == "Experience":
            experience_index = start
            
    # Calculate the score
    score = len(detected_categories) / 9
    
    # Check condition
    is_experience_first = True
    if "Education" in detected_categories and "Experience" in detected_categories:
        if education_index < experience_index:
            is_experience_first = False  # Education appears before Experience
    
    return score, detected_categories, is_experience_first





############################ Grade Functions ##############################




### Quantify Impact #####

def find_percentages(text):
    """Extract percentages from the given text."""
    
    # Regular expression pattern to match percentages
    pattern = r'(\d+(\.\d{1,2})?)%'
    
    # Find all matches
    matches = re.findall(pattern, text)
    
    # Extract the percentages without the capture group from the decimal places
    percentages = [match[0] for match in matches]
    if percentages:
        percentages = True;
    else:
        percentages = False;
    
    return percentages


### Unique Action Words ###

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


### Resume Length ####

def is_resume_over_three_quarters(parsed_resume_text):
    # Example heuristic: Assume an average page has 1000 words.
    words_per_page = 1000
    three_quarters_page_words = 0.75 * words_per_page

    # Count words in the parsed resume
    word_count = len(parsed_resume_text.split())

    return word_count > three_quarters_page_words


##### Use of Bullet Points & Presence & Length  #####

def check_bullets(text):
    bullet_points = [line.strip() for line in text.split('\n') if line.strip().startswith('•')]
    lines = text.split('\n')
    
    for line in lines:
        # Check if line starts with a bullet point
        if line.strip().startswith('•'):
            # Count number of sentences using a simple regex
            sentence_count = len(re.findall(r"[^.!?]*[.!?]", line))
            
            # Count number of lines based on newline characters after bullet
            line_count = len(line.split('\n'))
            
            if sentence_count > 2 or line_count > 2:
                bullet_sentence = False
            else:
                bullet_sentence = True;
    if bullet_points:
        bullet_points = True;
    else:
        bullet_points = False;
    # return bullet_points, bullet_sentence

    return bullet_points

######## Amount of pages ################
def get_pdf_page_count(pdf_path):
    return True
    

#### Consistencies #######


# def extract_font_info(pdf_path):
#     fonts = []

#     for page_layout in extract_pages(pdf_path):
#         for element in page_layout:
#             if isinstance(element, LTTextContainer):
#                 for text_line in element:
#                     for char in text_line:
#                         if isinstance(char, LTChar):
#                             fonts.append((char.fontname, char.size))

#     return fonts



# def check_font_consistency(pdf_path):
#     fonts = extract_font_info(pdf_path)

#     # Here, as an example, we'll simply see how many unique font sizes/types we have:
#     unique_fonts = set(fonts)

#     # You can then decide what "consistent" means. 
#     # For instance, if a PDF should use only 2 font sizes (e.g., header and body), then:
#     if len(unique_fonts) > 2:
#         return False
#     return True






###### GRAMMAR ######

# def has_mistakes(text):
#     my_tool = language_tool_python.LanguageTool('en-US')  

#     # getting the matches  
#     my_matches = my_tool.check(text)  
    
#     # defining some variables  
#     myMistakes = []  
    
#     # using the for-loop  
#     for rules in my_matches:  
#         if len(rules.replacements) > 0:  
#             myMistakes.append(text[rules.offset : rules.errorLength + rules.offset])  
    
#     # Return True if there are mistakes, False otherwise
#     return len(myMistakes) > 0




###### Avoid First Person Pronouns #######

def check_first_person_pronouns(text):
    # Define a list of first person pronouns
    pronouns = ["I", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"]

    # Use regex to match words to ensure that substrings inside other words aren't counted
    matches = []

    for pronoun in pronouns:
        pattern = r'\b' + pronoun + r'\b'  # Using word boundaries to ensure whole word match
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(pronoun)

    return matches

def calculate_grade(data):
    # Start with points from boolean checks
    grade_points = sum([
        data['quantify'],
        data['action'],
        data['threequarters'],
        # len(data['bulletcheck']) > 0,  # Assuming bulletcheck returns a list and you want to check if it's non-empty
        data['pagecount'] <= 2,  # Assuming 2 pages or less gets a point
        # data['consistency'],  # Uncomment once consistency is back in
        # not data['grammar'],  # Assuming grammar returns true for mistakes. So, we reverse the logic here.
        not data['firstperson'],  # Assuming firstperson returns true for usage of first-person pronouns. So, we reverse the logic.
        data['experiencefirst']
    ])

    # Add points from detected categories
    grade_points += sum(data['detected_categories'].values())

    # Define total possible points. Here it's 9 (from the boolean checks) + number of categories
    total_points = 9 + len(data['detected_categories'])

    # Calculate the grade in percentage
    grade_percentage = (grade_points / total_points) * 100

    return grade_percentage

@app.post("/convert-pdf-to-text/")
async def convert_pdf_to_text(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    pdf_path = temp_dir / file.filename
    with open(pdf_path, "wb") as pdf_file:
        shutil.copyfileobj(file.file, pdf_file)
    pdf_text = analyze_layout(pdf_path)  # Use the modified function here
    quantify = find_percentages(pdf_text)
    segments = extract_segments_from_text(pdf_text)
    grade, detected_categories, is_experience_first = grade_resume(pdf_text)
    action = check_action_words_in_text(actionWordsList=actionWordsList , text=pdf_text)
    threequarters = is_resume_over_three_quarters(pdf_text)
    bullet_check = check_bullets(pdf_text)
    page_count = get_pdf_page_count(pdf_path)
    # consistency = check_font_consistency(pdf_path)
    # grammar = has_mistakes(pdf_text)
    first_person = check_first_person_pronouns(pdf_text)
    detected_dict = {category: category in detected_categories for category in categories}
    grade_percentage = calculate_grade({
    "detected_categories": detected_dict, 
    'quantify': quantify, 
    "action": action, 
    "threequarters": threequarters, 
    "bulletcheck": bullet_check,
    "pagecount": page_count,
    # "grammar": grammar,
    "firstperson": first_person,
    "experiencefirst": is_experience_first
    })
    shutil.rmtree(temp_dir)
    return {
        "pdf_text": pdf_text, 
        "segments": segments, 
        "grade": grade, 
        "detected_categories": detected_dict, 
        'quantify': quantify, 
        "action": action, 
        "threequarters": threequarters, 
        "bulletcheck": bullet_check,
        "pagecount": page_count,
        # "consistency": consistency,
        # "grammar": grammar,
        "firstperson": first_person,
        "experiencefirst": is_experience_first,
        "overallgrade": grade_percentage
        }







































