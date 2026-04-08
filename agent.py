import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.messages import HumanMessage
from tools import tools

load_dotenv()

llm= ChatGroq(
    model="llama3-70b-8192",
    temperature=0.7,
    api_key = os.getenv("GROQ_API_KEY")
)


#Loading the react prompt template
prompt = hub.pull("hwchase17/react")

#Building ReAct Agent

agent = create_react_agent(
    llm= llm,
    tools = tools,
    prompt = prompt
)

#Wrapping in Agent Executor

agent_executor= AgentExecutor(
    agent= agent,
    tools= tools,
    verbose = True,
    handle_parsing_errors = True,
    max_iterations = 10
)

# Main Function

def run_agent(job_desc: str):
    """
    Takes a job description as input and runs the full ReAct agent loop.
    The agent will read your CV, tailor it, write a cover letter, and save everything.
    """

    print("\n" + "="*60)
    print("   JOB APPLICATION AGENT STARTING")
    print("="*60 + "\n")


    task = f"""

    You are a job application assistant. Complete the following task step by step:
    
    1. First, read the user's CV using the read_cv tool
    2. Then tailor the CV for this specific job description using the tailor_cv tool
    3. Then write a cover letter using the write_cover_letter tool
    4. Finally save both documents using the save_files tool
    
    The job description is:
    {job_desc}
    
    Make sure to complete ALL 4 steps. Do not stop until files are saved.

    """

    result = agent_executor.invoke(
        {
            "input" : task
        }
    )


    print("\n" + "="*60)
    print("   AGENT FINISHED")
    print("="*60 + "\n")
    
    print("FINAL OUTPUT:")
    print(result["output"])

    return result["output"]


# Entry Point

if __name__ == "__main__":

    print("Paste the job description below.")
    print("When done, type END on a new line and press Enter:\n")

    lines=[]

    while True:

        line = input()

        if line.strip() == "END":
            break

        lines.append(line)


    job_desc = "\n".join(lines)


    if not job_desc.strip():
        # if the user typed nothing at all
        print("No job description provided. Please try again.")
    else:
        run_agent(job_desc)    

