import os                    
from datetime import date    
from dotenv import load_dotenv         
from groq import Groq
from langchain_core.tools import tool
from email.message import EmailMessage
import smtplib
import json
import requests


load_dotenv()

MEMORY={}

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

def call_llm(prompt: str) -> str:

    """
    Sends a prompt to Groq and returns the response text.
    """

    response = client.chat.completions.create(
        model = MODEL,
        messages=[
            {
                "role" : "user",
                "content" : prompt
            }
        ],
        temperature = 0,
        max_tokens=800
    )

    return response.choices[0].message.content

# Tool -1: Read CV

@tool
def read_cv(cv : str = "") -> str:
    
    """
    Reads the user's CV from the my_cv.txt file and returns it as text.
    Use this tool first before doing anything else.
    """

    print("Read CV called")

    try:
        with open("my_cv.txt","r",encoding="utf-8") as file:
            content= file.read()
            return content
        
    except FileNotFoundError:

        return "The CV file is not found. Please send the file again and re-try"
    

# Tool -2 : Tailor CV

@tool
def tailor_cv(cv_text: str, job_description: str) -> str:

    """
    Takes the user's original CV and a job description as input,
    and returns a tailored version of the CV that matches the job requirements.
    """  


    print("Tailor Cv called")

    cv_text = cv_text[:1200]
    job_description = job_description[:1200]

    prompt= f"""

       Rewrite the CV professionally for this job.

Make it detailed, structured, and strong.

CV:
{cv_text}

JOB:
{job_description}

Return a complete improved CV with sections:
- Summary
- Experience
- Skills
- Education


        """

    output= call_llm(prompt)

    MEMORY["tailored_cv"] = output

    return "tailored_cv_saved"
    

# Tool - 3: Write Cover Letter

@tool
def draft_cover_letter(tailored_cv: str, job_description: str) -> str:

    """
    Takes the tailored CV and job description and writes a professional cover letter.
    """

    print("draft_cover_letter called")


    tailored_cv = tailored_cv[:1200]
    job_description = job_description[:1200]

    cv_text = MEMORY.get("tailored_cv", "")


    prompt= f"""

        Write a strong professional cover letter.

Use proper format:
- Greeting
- Body
- Closing

CV:
{cv_text}

JOB:
{job_description}

Make it detailed and personalized.

        """


    output = call_llm(prompt)

    MEMORY["cover_letter"] = output

    return "cover_letter_saved"
        
    
@tool
def save_file(cv_text: str, cover_letter: str) -> str:

    """
    Saves the tailored CV and cover letter to the outputs folder as text files.
    """
    
    print("save_file called")


    try:

        cv_text = MEMORY.get("tailored_cv", "")
        cover_letter = MEMORY.get("cover_letter", "")

        if len(cv_text.strip()) < 50:
            return "ERROR: CV content missing or too small"

        if len(cover_letter.strip()) < 50:
            return "ERROR: Cover letter content missing or too small"

        today = date.today().strftime("%Y-%m-%d")


        base_dir = os.path.abspath("outputs")

        os.makedirs(base_dir, exist_ok=True)

        cv_path = os.path.join(base_dir, f"tailored_cv_{today}.txt")
        cover_path = os.path.join(base_dir, f"cover_letter_{today}.txt")

        with open(cv_path, "w", encoding = "utf-8") as file:
            file.write(cv_text)

        with open(cover_path, "w", encoding="utf-8") as file:
            file.write(cover_letter)

        
        print("Files saved at:", cv_path, cover_path)

        return f"{cv_path}|{cover_path}"
    
    except Exception as e:
        return f"Error saving files: {str(e)}"
    

@tool
def send_email(file_paths: str) ->str:
    
    """
    Sends the generated CV and cover letter to the recruiter via email.
    """    

    print("send_email called")

    print("RAW INPUT:", file_paths)

    try:
        cv_path, cover_letter_path = file_paths.split("|")
    except Exception as e:
        return f"ERROR parsing file paths: {str(e)}"

    print("Parsed paths:", cv_path, cover_letter_path)

    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD') 
    receiver = os.getenv('EMAIL_RECEIVER')

    msg = EmailMessage()

    msg['Subject'] = "AI/Ml Developer Application"
    msg['From'] = sender
    msg['To'] = receiver

    msg.set_content("Hi,\n\nPlease find my CV and cover letter attached.\n\nRegards")

    #Attach CV
    with open(cv_path, 'r', encoding='utf-8') as f:
        print("CV CONTENT PREVIEW:", f.read()[:100])
        msg.add_attachment(f.read(), maintype="application", subtype='octet-stream', filename='CV.txt')

    #Attaching cover letter
    with open(cover_letter_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename="CoverLetter.txt")


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    return "FINAL ANSWER: Email sent successfully with CV and cover letter."    


@tool
def get_company_info(company_name: str) -> str:
    """
    Fetch company information from MCP server.
    """

    try:

        response = requests.post(
            "http://127.0.0.1:8000/get_company_info",
            json={"company_name": company_name}
        )

        return response.json()['info']
    
    except Exception as e:
        return f"Error fetching company info: {str(e)}"

    
