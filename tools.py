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

# Tool -1: Read CV

@tool
def read_cv(cv : str = "") -> str:
    
    """
    Reads the user's CV from my_cv.txt and returns the full text.
    Call this SECOND, after get_company_info.
    No input needed — pass an empty string.
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
    Rewrites the user's CV to match a specific job description.
    Call this THIRD.
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

    output= call_llm(prompt)

    MEMORY["tailored_cv"] = output

    return "tailored_cv_saved"
    

# Tool - 3: Write Cover Letter

@tool
def draft_cover_letter(tailored_cv: str, job_description: str) -> str:

    """
    Writes a professional cover letter based on the tailored CV and job description.
    Call this FOURTH.
    Inputs:
    - tailored_cv: pass the string "tailored_cv_saved" here
    - job_description: the original job description from the user
    Returns: cover_letter_saved
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
    Saves the tailored CV and cover letter as text files in the outputs folder.
    Call this FIFTH.
    Inputs:
    - cv_text: pass the string "tailored_cv_saved" here
    - cover_letter: pass the string "cover_letter_saved" here
    Returns: two file paths joined by | like: path1|path2
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
    Sends the saved CV and cover letter to the recruiter by email.
    Call this SIXTH and LAST.
    Input:
    - file_paths: the EXACT string returned by save_file, formatted as path1|path2
    Do NOT modify this string in any way before passing it in.
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


    print("SENDER:", sender)
    print("PASSWORD EXISTS:", bool(password))
    print("RECEIVER:", receiver)

    msg = EmailMessage()

    msg['Subject'] = "AI/Ml Developer Application"
    msg['From'] = sender
    msg['To'] = receiver

    msg.set_content("Hi,\n\nPlease find my CV and cover letter attached.\n\nRegards")

    #Attach CV
    with open(cv_path, 'r', encoding='utf-8') as f:
        content= f.read()
        print("CV CONTENT PREVIEW:", content[:100])
        msg.add_attachment(content.encode('utf-8'), maintype="application", subtype='octet-stream', filename='CV.txt')

    #Attaching cover letter
    with open(cover_letter_path, 'r', encoding='utf-8') as f:
        cover_content = f.read()
        msg.add_attachment(cover_content.encode('utf-8'), maintype="application", subtype="octet-stream", filename="CoverLetter.txt")


    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)

    except Exception as e:
        print("EMAIL ERROR:", str(e))
        return f"ERROR sending email: {str(e)}"        

    return "FINAL ANSWER: Email sent successfully with CV and cover letter."    


@tool
def get_company_info(company_name: str) -> str:
    
    """
    Searches the web for real information about a company.
    Call this FIRST before any other tool.
    Input:
    - company_name: extract this from the job description.
      If no company name is found, use "Unknown Company"
    Returns: a text summary of the company.
    """


    print("get_company_info called for company: ",company_name)

    try:

        response = requests.post(
            "http://127.0.0.1:8000/get_company_info",
            json={"company_name": company_name},
            timeout=10
        )

        if response.status_code==200:
            info = response.json().get("info","No info provided")
            print("Info received about company", info[:200])
            return info
        
        else:
            return f"MCP server returned error {response.status_code} for {company_name}"
        
    except requests.exceptions.ConnectionError:

        return "ERROR: MCP server is not running. Please start it with: uvicorn mcp_server:app --reload"

    except requests.exceptions.Timeout:

        return f"ERROR: MCP server timed out while fetching info for {company_name}"    
    
    except Exception as e:
        return f"Error fetching company info: {str(e)}"

    
