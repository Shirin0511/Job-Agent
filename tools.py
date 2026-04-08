import os                    
from datetime import date    
from dotenv import load_dotenv         
from langchain_groq import ChatGroq     
from langchain.tools import tool

load_dotenv()

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0.7,
    api_key= os.getenv('GROQ_API_KEY')
)

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
def tailor_cv(input_txt: str) -> str:

    """
    Takes the user's original CV and a job description as input,
    and returns a tailored version of the CV that matches the job requirements.
    Input should be formatted as: CV: [cv content] ||| JOB: [job description]
    """  

    try:

        parts= input_txt.split("|||")

        if len(parts)!=2:
            return "Error: Please provide input as 'CV: [content] ||| JOB: [job description]'"

        cv_text = parts[0].replace("CV:","").strip()

        job_text = parts[1].replace("JOB:","").strip()

        prompt= f"""

        You are a professional CV writer and career coach.
        
        Here is the candidate's original CV:
        {cv_text}
        
        Here is the job description they are applying for:
        {job_text}
        
        Your task:
        1. Rewrite the CV to highlight skills and experiences most relevant to this job
        2. Use keywords from the job description naturally in the CV
        3. Keep all information truthful — do not invent experience
        4. Keep the same basic structure but make it feel targeted to this role
        5. Return ONLY the tailored CV text, nothing else


        """

        response = llm.invoke(prompt)  

        return response.content
    
    except Exception as e:
        return f"Error tailoring CV: {str(e)}"
    

# Tool - 3: Write Cover Letter


@tool
def draft_cover_letter(input_txt: str) -> str:

    """
    Takes the tailored CV and job description and writes a professional cover letter.
    Input should be formatted as: CV: [tailored cv] ||| JOB: [job description]
    """

    try:

        parts = input_txt.split("|||")

        if len(parts)!=2:
            return "Error: Please provide input as  CV: [tailored cv] ||| JOB: [job description]"
        
        cv_text = parts[0].replace("CV:","").strip()

        job_text = parts[1].replace("JOB:","").strip()

        prompt= f"""

        You are an expert cover letter writer.
        
        Here is the candidate's tailored CV:
        {cv_text}
        
        Here is the job description:
        {job_text}
        
        Write a compelling, professional cover letter that:
        1. Opens with a strong hook — not "I am writing to apply for..."
        2. Shows genuine enthusiasm for this specific role and company
        3. Connects 2-3 specific experiences from the CV to the job requirements
        4. Is concise — maximum 4 paragraphs
        5. Ends with a confident call to action
        6. Sounds human and natural, not robotic
        
        Return ONLY the cover letter text, nothing else.

        """

        response = llm.invoke(prompt)

        return response.content
    
    except Exception as e:
       
        return f"Error in drafting cover letter: {str(e)}"
    


@tool
def save_file(input_txt: str) -> str:

    """
    Saves the tailored CV and cover letter to the outputs folder as text files.
    Input should be formatted as: CV: [tailored cv content] ||| LETTER: [cover letter content]
    """

    try:

        parts= input_txt.split("|||")

        if len(parts)!=2:
            return "Error: Please provide input as 'CV: [cv content] ||| LETTER: [letter content]'"
    

        cv_content = parts[0].replace("CV:","").strip()

        letter_content = parts[1].repalce("LETTER:","").strip()

        today = date.today().strftime("%Y-%m-%d")


        cv_file = f"outputs/tailored_cv_{today}.txt"
        letter_file = f"outputs/cover_letter_{today}.txt"

        with open(cv_file, "w", encoding = "utf-8") as file:
            file.write(cv_content)

        with open(letter_file, "w", encoding="utf-8") as file:
            file.write(letter_content)

        return f"Files saved successfully!\n- {cv_file}\n- {letter_file}"
    
    except Exception as e:
        return f"Error saving files: {str(e)}"
    

# Exporting Tools

tools = [read_cv, tailor_cv, draft_cover_letter, save_file]    

        



