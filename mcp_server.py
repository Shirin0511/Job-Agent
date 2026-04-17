from fastapi import FastAPI
from pydantic import BaseModel
from duckduckgo_search import DDGS

app= FastAPI()

class CompanyRequest(BaseModel):

    company_name: str

@app.post("/get_company_info")
def get_company_info(req: CompanyRequest):

    """
    Searches DuckDuckGo for real information about a company
    and returns a summary that the agent can use to personalize
    the cover letter.
    """

    company = req.company_name.strip()

    if not company:
        return {
            "company_name" : company,
            "info" : "No company name provided"
        }
    
    try:

        results= []

        with DDGS() as ddgs:

            search_query = f"{company} company overview culture tech stack work environment"

            for result in ddgs.text(search_query, max_results=5):

                snippet = result.get("body","")

                if snippet:
                    results.append(snippet)

        if not results:
            return {
                    "company_name" : company,
                    "info" : f"No information found about {company}"
                }     

        combined = "\n\n".join(results) 

        final_info = f"Company: {company} \n\n {combined}"  

        return {
            "company_name" : company,
            "info" : final_info
        }
    
    except Exception as e:

        return {
            "company_name" : company,
            "info" : f"Couldn't fetch info about {company}"
        }

