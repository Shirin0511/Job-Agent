import os                    
from datetime import date    
from dotenv import load_dotenv         
from groq import Groq
from langchain_core.tools import tool
from email.message import EmailMessage
import smtplib
import json


load_dotenv()

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

    cv_text = cv_text[:1200]
    job_description = job_description[:1200]

    prompt= f"""

        Rewrite this CV to match the job description.

CV:
{cv_text}

JOB:
{job_description}

Return only the improved CV.


        """

    return call_llm(prompt)

    

# Tool - 3: Write Cover Letter

@tool
def draft_cover_letter(cv_text: str, job_description: str) -> str:

    """
    Takes the tailored CV and job description and writes a professional cover letter.
    """
    cv_text = cv_text[:1200]
    job_description = job_description[:1200]

    prompt= f"""

        Write a short professional cover letter using this CV and job.

CV:
{cv_text}

JOB:
{job_description}

Keep it concise and relevant.

        """

    return call_llm(prompt)
        
    
@tool
def save_file(cv_text: str, cover_letter: str) -> str:

    """
    Saves the tailored CV and cover letter to the outputs folder as text files.
    """

    try:
        today = date.today().strftime("%Y-%m-%d")


        cv_path = f"outputs/tailored_cv_{today}.txt"
        cover_path = f"outputs/cover_letter_{today}.txt"

        with open(cv_path, "w", encoding = "utf-8") as file:
            file.write(cv_text)

        with open(cover_path, "w", encoding="utf-8") as file:
            file.write(cover_letter)


        return json.dumps({
            "cv_path": cv_path,
            "cover_letter_path": cover_path,
            "status": "success"
        })
    
    except Exception as e:
        return f"Error saving files: {str(e)}"
    

@tool
def send_email(cv_path: str, cover_letter_path:str) ->str:
    
    """
    Sends the generated CV and cover letter to the recruiter via email.
    """    
    
    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD') 
    receiver = os.getenv('EMAIL_RECEIVER')

    msg = EmailMessage()

    msg['Subject'] = "AI/Ml Developer Application"
    msg['From'] = sender
    msg['To'] = receiver

    msg.set_content("Hi,\n\nPlease find my CV and cover letter attached.\n\nRegards")

    #Attach CV
    with open(cv_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype="application", subtype='octet-stream', filename='CV.txt')

    #Attaching cover letter
    with open(cover_letter_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename="CoverLetter.txt")


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    return "FINAL ANSWER: Email sent successfully with CV and cover letter."    


    
