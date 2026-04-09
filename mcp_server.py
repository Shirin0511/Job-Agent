from fastapi import FastAPI
from pydantic import BaseModel

app= FastAPI()

class CompanyRequest(BaseModel):

    company_name: str

@app.post("/get_company_info")
def get_company_info(req: CompanyRequest):

    data= {
        "Google": "Tech company focused on search, cloud, and AI.",
        "Amazon": "E-commerce and cloud computing company.",
        "Microsoft": "Software and cloud services company.",
        "OpenAI": "AI research company focused on large language models."
        }

    return {
            "company_name" : req.company_name,
            "info" : data.get(req.company_name,"No information available")
    }
