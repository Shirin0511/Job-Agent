import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from tools import tools

load_dotenv()

llm= ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    api_key = os.getenv("GROQ_API_KEY")
)


system_prompt= f"""You are a job application assistant.

When given a job description, you MUST complete all 4 steps in this exact order:

Step 1 - Use the read_cv tool to read the user's CV. Pass an empty string "" as input.
Step 2 - Use the tailor_cv tool. Format input exactly as: CV: [cv text] ||| JOB: [job description]
Step 3 - Use the write_cover_letter tool. Format input exactly as: CV: [tailored cv] ||| JOB: [job description]  
Step 4 - Use the save_files tool. Format input exactly as: CV: [tailored cv] ||| LETTER: [cover letter]

Do not stop until all 4 steps are complete and files are saved.
Always follow the exact input format for each tool."""

#Building ReAct Agent

agent = create_react_agent(
    mdoel= llm,
    tools = tools,
    prompt = system_prompt
)

# Main Function

def run_agent(job_desc: str):
    """
    Runs the full ReAct agent loop for a given job description.

    """

    print("\n" + "="*60)
    print("   JOB APPLICATION AGENT STARTING")
    print("="*60 + "\n")


    result = agent.invoke(
        {
            "messages" : [
            HumanMessage(content= "Please process this job description and complete all 4 steps:\n\n{job_desc}")
            ]
        }
    )


    print("\n" + "="*60)
    print("   AGENT FINISHED")
    print("="*60 + "\n")
    
    for i, message in enumerate(result['messages']):

        type_name = type(message).__name__

        print(f"Step {i+1} [{type_name}]")
        print("-" * 40)

        content = message.content

        if isinstance(content, str) and content.strip():

            if len(content)>600:
                print(content[:600])

            else:
                print(content)    

        elif isinstance(content,list):

            for block in content:
                if isinstance(block, dict):
                    if block.get("type")=="text" and block.get("text","").strip():
                        text = block["text"]
                        print(text[:600] + "\n... [truncated] ..." if len(text) > 600 else text)
                    elif block.get("type") =="tool_use":
                        print(f"Calling tool: {block.get('name')}")
                        inp = str(block.get('input',''))
                        print(f"With input: {inp[:300]}..." if len(inp) > 300 else f"With input: {inp}")

        print()

        print("="*60)
    print("   DONE — check your outputs/ folder!")
    print("="*60 + "\n")
    
    last_message = result["messages"][-1]
    
    if hasattr(last_message, 'content') and last_message.content:
        print("Agent's final message:")
        print(last_message.content)  
          


# Entry Point

if __name__ == "__main__":

    print("Paste the job description below.")
    print("When done, type END on a new line and press Enter:\n")

    lines=[]

    while True:

        try: 
            line = input()

            if line.strip() == "END":
                break

            lines.append(line)

        except KeyboardInterrupt:
            print("\nCancelled by user.")
            break    


    job_desc = "\n".join(lines)


    if not job_desc.strip():
        # if the user typed nothing at all
        print("No job description provided. Please try again.")
    else:
        run_agent(job_desc)    

