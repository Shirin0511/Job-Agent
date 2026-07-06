import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import read_cv, tailor_cv, draft_cover_letter, save_file, send_email, get_company_info

load_dotenv()

# LLM
llm = ChatGroq(
model="llama-3.3-70b-versatile",
#model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# Tools list
tools = [read_cv, tailor_cv, draft_cover_letter, save_file, get_company_info]

# Create agent
agent = create_react_agent(
    model=llm,
    tools=tools
)

# Run loop
while True:
    user_input = input("\nEnter job description (or 'exit'): ")

    if user_input.lower() == "exit":
        break

    user_input = user_input[:1500]

    response = agent.invoke(
    {
        "messages": [
            {
            "role": "system",
    "content": """

    You are a job application assistant. You MUST call tools in this exact order:

1. get_company_info — extract company name from job description and call this first
2. read_cv — read the user's CV
3. tailor_cv — tailor the CV using cv_text and job_description
4. draft_cover_letter — write cover letter using tailored_cv and job_description
5. save_file — save both documents, pass "tailored_cv_saved" and "cover_letter_saved"

RULES:
- Call every tool exactly once
- Do not skip any tool
- Do not generate text yourself
- After save_file, respond with: FINAL ANSWER: Draft ready for review
  followed on new lines by:
  TAILORED_CV_PATH: <path returned by save_file>
  COVER_LETTER_PATH: <path returned by save_file>
    
    """

},
            
            {"role": "user", 
            "content": user_input}
        ]
    },
    config={"recursion_limit": 25}
    )

    final_op = response['messages'][-1].content

    if "FINAL ANSWER" not in final_op:
        print("\n[Agent did not complete the draft pipeline — not proceeding to send.]")
        continue

    cv_path, cl_path = extract_paths(final_op)

    if not cv_path or cl_path:
        print("\n[Could not extract file paths from agent output — stopping before send for safety.]")
        continue

    decision = get_human_approval(cv_path, cl_path)

    if decision =='y':
        try:
            result = send_email(cv_path,cl_path)
            print("Email Sent Successfully")
            print(result)

        except Exception as e:
            print("Sending Email Failed")  

    elif decision == "e":
        print("\n[Edit-and-retry not wired up yet — for now, adjust the job description and rerun.]")
    else:
        print("\n[Skipped — nothing was sent.]")          



    print("\nFinal Output:\n")
    print(response["messages"][-1].content)


def get_human_approval(cv_path, cover_letter_path):
    """Show the drafted content and get explicit sign-off before anything is sent."""
    print("\n" + "="*60)
    print("REVIEW REQUIRED BEFORE SENDING")
    print("="*60)

    try:
        with open(cv_path,"r") as f:
            print("Tailored CV: ")
            print(f.read())

    except Exception as e:
        print(f"[Could not read CV at {cv_path}: {e}]")        

    try:
        with open(cover_letter_path, "r") as f:
            print("\n--- COVER LETTER ---\n")
            print(f.read())
    except Exception as e:
        print(f"[Could not read cover letter file at {cover_letter_path}: {e}]")

    while True:
        decision = input("Send this application? [y]es / [n]o / [e]dit-n-retry: ")
        if decision in ('y','r','e'):
            return decision
        print("Please type y, n or e")


def extract_paths(final_text):
    """Pull the two file paths out of the agent's final answer text."""
    cv_path, cl_path = None, None

    for line in final_text.splitlines():
        if line.startswith("TAILORED_CV_PATH:"):
            cv_path = line.split(":",1)[1].strip()
        elif line.startwith("COVER_LETTER_PATH:"):
            cl_path = line.split(":",1)[1].strip()

    return cv_path, cl_path




        
