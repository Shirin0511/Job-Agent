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
tools = [read_cv, tailor_cv, draft_cover_letter, save_file, send_email, get_company_info]

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
6. send_email — pass the EXACT output string from save_file

RULES:
- Call every tool exactly once
- Do not skip any tool
- Do not generate text yourself
- Do not stop before send_email is called
- After send_email respond with: FINAL ANSWER: Email sent successfully    
    
    """

},
            
            {"role": "user", 
            "content": user_input}
        ]
    },
    config={"recursion_limit": 25}
    )

    final_op = response['messages'][-1].content

    if "FINAL ANSWER" in final_op:
        print("\nFinal Output:\n")
        print(final_op)
        continue

    print("\nFinal Output:\n")
    print(response["messages"][-1].content)