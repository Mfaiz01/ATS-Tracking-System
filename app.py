import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Templates
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

skills_prompt_template = """
How can I improve my skills based on the following resume?

Resume:
{text}
"""

match_prompt_template = """
What is the percentage match of the following resume for the job description?

Resume:
{text}

Job Description:
{jd}
"""

formatting_prompt_template = """
What are some formatting tips to improve the following resume?

Resume:
{text}
"""

optimization_tips_prompt = """
Provide tips for optimizing a resume for ATS based on the following resume.

Resume:
{text}
"""

# Streamlit app
st.title("CareerPath ATS")
st.text("Improve Your Resume for ATS")

# Input fields
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if submit:
    if uploaded_file is not None:
        # Extract text from uploaded PDF
        text = input_pdf_text(uploaded_file)
        
        # Format prompt
        formatted_prompt = input_prompt.format(text=text, jd=jd)
        
        # Get response from Gemini
        response = get_gemini_response(formatted_prompt)
        
        try:
            # Parse the JSON response
            response_data = json.loads(response)
            jd_match = response_data.get("JD Match", "N/A")
            missing_keywords = response_data.get("MissingKeywords", [])
            profile_summary = response_data.get("Profile Summary", "N/A")
            
            # Display the response in a human-readable format
            st.subheader("Job Description Match Percentage")
            st.write(f"{jd_match}")
            
            st.subheader("Missing Keywords")
            st.write(", ".join(missing_keywords) if missing_keywords else "None")
            
            st.subheader("Profile Summary")
            st.write(profile_summary)

            # Set session state to show additional buttons
            st.session_state.submitted = True
            st.session_state.resume_text = text
            st.session_state.jd_text = jd
            
        except json.JSONDecodeError:
            st.error("Failed to parse the response. Please try again.")

# Show additional buttons if the first submission is done
if st.session_state.submitted:
    improvise_skills = st.button("How Can I Improve My Skills")
    percentage_match = st.button("Percentage Match")
    formatting_tips = st.button("Resume Formatting Tips")
    optimization_tips = st.button("ATS Optimization Tips")
    
    if improvise_skills:
        # Functionality for "How Can I Improve My Skills"
        skills_prompt = skills_prompt_template.format(text=st.session_state.resume_text)
        skills_response = get_gemini_response(skills_prompt)
        st.subheader("Skills Improvement Suggestions")
        st.write(skills_response)
        
    if percentage_match:
        # Functionality for "Percentage Match"
        match_prompt = match_prompt_template.format(text=st.session_state.resume_text, jd=st.session_state.jd_text)
        match_response = get_gemini_response(match_prompt)
        st.subheader("Percentage Match")
        st.write(match_response)

    if formatting_tips:
        # Functionality for "Resume Formatting Tips"
        formatting_prompt = formatting_prompt_template.format(text=st.session_state.resume_text)
        formatting_response = get_gemini_response(formatting_prompt)
        st.subheader("Resume Formatting Tips")
        st.write(formatting_response)
        
    if optimization_tips:
        # Functionality for "ATS Optimization Tips"
        optimization_prompt = optimization_tips_prompt.format(text=st.session_state.resume_text)
        optimization_response = get_gemini_response(optimization_prompt)
        st.subheader("ATS Optimization Tips")
        st.write(optimization_response)
