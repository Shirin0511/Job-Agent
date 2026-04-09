import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import read_cv, tailor_cv, draft_cover_letter, save_file, send_email, get_company_info

load_dotenv()

# LLM
llm = ChatGroq(
#model="llama-3.3-70b-versatile",
model="llama-3.1-8b-instant",
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
               You are a job assistant that MUST use tools to complete the task.

STRICT RULES:
- You MUST call tools, do NOT generate answers yourself
- NEVER return text without using tools
- ALWAYS pass outputs between tools correctly

EXECUTION PLAN:
1. Call read_cv → get cv_text
2. Call tailor_cv(cv_text, job_description)
3. Call draft_cover_letter(tailored_cv, job_description)
4. Call save_file(tailored_cv, cover_letter)
5. Call send_email(send_email)

IMPORTANT:
- Do NOT skip any step
- Do NOT repeat steps
- Do NOT hallucinate outputs
- STOP after send_email

FINAL OUTPUT:
Return ONLY:
FINAL ANSWER: Email sent successfully
"""
},
            
            {"role": "user", 
            "content": user_input}
        ]
    },
    config={"recursion_limit": 10}
    )

    final_op = response['messages'][-1].content

    if "FINAL ANSWER" in final_op:
        print("\nFinal Output:\n")
        print(final_op)
        continue

    print("\nFinal Output:\n")
    print(response["messages"][-1].content)