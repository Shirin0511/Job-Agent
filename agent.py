import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import read_cv, tailor_cv, draft_cover_letter, save_file, send_email

load_dotenv()

# LLM
llm = ChatGroq(
#model="llama-3.3-70b-versatile",
model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# Tools list
tools = [read_cv, tailor_cv, draft_cover_letter, save_file, send_email]

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
                You are a job assistant.

Use tools in order:
1. read_cv
2. tailor_cv
3. draft_cover_letter
4. save_file
5. send_email

Pass real outputs between tools.
Do not use placeholders.
Stop after email.
                """
},
            
            {"role": "user", 
            "content": user_input}
        ]
    },
    config={"recursion_limit": 15}
    )

    print("\nFinal Output:\n")
    print(response["messages"][-1].content)