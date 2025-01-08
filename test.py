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
import language_tool_python  

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


pdf_path = '/Users/brandonluffman/resumeparserofficial/resume.pdf'
text = analyze_layout(pdf_path)

def has_mistakes(text):
    my_tool = language_tool_python.LanguageTool('en-US')  

    # getting the matches  
    my_matches = my_tool.check(text)  
    
    # defining some variables  
    myMistakes = []  
    
    # using the for-loop  
    for rules in my_matches:  
        if len(rules.replacements) > 0:  
            myMistakes.append(text[rules.offset : rules.errorLength + rules.offset])  
    
    print('Grammar Mistakes', myMistakes)
    # Return True if there are mistakes, False otherwise
    return len(myMistakes) > 0

# print(text)

print(has_mistakes(text))