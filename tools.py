import os                    
from datetime import date    
from dotenv import load_dotenv         
from groq import Groq
from langchain_core.tools import tool
from email.message import EmailMessage
import smtplib
import json
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#MODEL = "llama-3.1-8b-instant"
MODEL="llama-3.3-70b-versatile"



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


def extract_company_name(job_description: str) -> str:

    prompt = f""" Extract only company name from the job description.

    If no company name is present, respond with exactly: Unknown Company
    
    Respond with only the company name.

    JOB DESCRIPTION :
    {job_description[:1000]}"""

    result = call_llm(prompt).strip()

    return result if result else "Unknown Company"
    


def read_cv() -> str:
    
    """
    Reads the user's CV from my_cv.txt and returns the full text.
    No input needed — pass an empty string.
    """

    print("Read CV called")

    try:
        with open("my_cv.txt","r",encoding="utf-8") as file:
            content= file.read()
            return content
        
    except FileNotFoundError:

        return "The CV file is not found. Please send the file again and re-try"
    

def tailor_cv(cv_text: str, job_description: str) -> str:

    """
    Rewrites the user's CV to match a specific job description.
    Inputs:
    - cv_text: the full CV text returned by read_cv
    - job_description: the original job description from the user
    Returns: tailored_cv_saved
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

    return call_llm(prompt)
    

def draft_cover_letter(tailored_cv: str, job_description: str, company_info : str) -> str:

    """
    Writes a professional cover letter based on the tailored CV and job description.
    Inputs:
    - tailored_cv: pass the string "tailored_cv_saved" here
    - job_description: the original job description from the user
    Returns: cover_letter_saved
    """
   
    print("draft_cover_letter called")


    tailored_cv = tailored_cv[:1200]
    job_description = job_description[:1200]

    prompt= f"""

        Write a strong professional cover letter.

Use proper format:
- Greeting
- Body
- Closing

CV:
{tailored_cv}

COMPANY INFORMATION:
{company_info}

JOB:
{job_description}

Make it detailed and personalized.

        """


    return call_llm(prompt)        
    

def text_to_pdf(text: str, output_path: str, title: str = None):
    
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch
    )
    styles = getSampleStyleSheet()
    story = []
    if title:
        story.append(Paragraph(title, styles['Heading1']))
        story.append(Spacer(1, 12))
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 8))
            continue
        safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe_line, styles['Normal']))
    doc.build(story)
   


def save_file(tailored_cv: str, cover_letter: str) -> tuple[str, str]:

    """
    Saves the tailored CV and cover letter as text files in the outputs folder.
    Inputs:
    - cv_text: pass the string "tailored_cv_saved" here
    - cover_letter: pass the string "cover_letter_saved" here
    Returns: two file paths joined by | like: path1|path2
    """
    
    print("save_file called")

    today = date.today().strftime("%Y-%m-%d")
    base_dir = os.path.abspath("outputs")
    os.makedirs(base_dir, exist_ok=True)

    cv_path = os.path.join(base_dir, f"tailored_cv_{today}.pdf")
    cover_path = os.path.join(base_dir, f"cover_letter_{today}.pdf")

    text_to_pdf(tailored_cv, cv_path, title = "Tailored CV")
    text_to_pdf(cover_letter, cover_path, title= "Cover Letter")

    return cv_path, cover_path
    


def send_email(cv_path: str, cl_path:str) ->str:
    
    """
    Sends the saved CV and cover letter to the recruiter by email.
    Input:
    - file_paths: the EXACT string returned by save_file, formatted as path1|path2
    Do NOT modify this string in any way before passing it in.
    """    

    print("send_email called")    


    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD') 
    receiver = os.getenv('EMAIL_RECEIVER')


    print("SENDER:", sender)
    print("PASSWORD EXISTS:", bool(password))
    print("RECEIVER:", receiver)

    msg = EmailMessage()

    msg['Subject'] = "AI/Ml Developer Application"
    msg['From'] = sender
    msg['To'] = receiver

    msg.set_content("Hi,\n\nPlease find my CV and cover letter attached.\n\nRegards")

    #Attach CV
    with open(cv_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype="application", subtype='pdf', filename='CV.pdf')

    #Attaching cover letter
    with open(cl_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="CoverLetter.pdf")


    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)

    except Exception as e:
        print("EMAIL ERROR:", str(e))
        raise      

    return "FINAL ANSWER: Email sent successfully with CV and cover letter."    



def get_company_info(company_name: str) -> tuple[str, bool]:
    
    """
    Searches the web for real information about a company.
    Input:
    - company_name: extract this from the job description.
      If no company name is found, use "Unknown Company"
    Returns: a text summary of the company.
    """

    if not company_name or company_name.strip().lower() == "unknown company":
        return "No company name was identified in the job description, so company research was skipped.", False

    try:

        response = requests.post(
            "http://127.0.0.1:8000/get_company_info",
            json={"company_name": company_name},
            timeout=10
        )

        if response.status_code==200:
            info = response.json().get("info","No info provided"), False
            print("Info received about company", info[:200])
            return info
        
        else:
            error_msg =  f"MCP server returned error {response.status_code} for {company_name}", True
            return error_msg
        
    except requests.exceptions.ConnectionError:

        error_msg=  "ERROR: MCP server is not running. Please start it with: uvicorn mcp_server:app --reload", True
        return error_msg

    except requests.exceptions.Timeout:

        error_msg = f"ERROR: MCP server timed out while fetching info for {company_name}" , True
        return error_msg   
    
    except Exception as e:
        error_msg =  f"Error fetching company info: {str(e)}", True
        return error_msg

    
