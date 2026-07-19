from langgraph.graph import StateGraph, START, END
from state import AgentState
import tools

def extract_company_node(state: AgentState)-> dict:
    print("Extarcting Company Name")
    company_name = tools.extract_company_name(state['job_description'])
    print("Company Name: ", company_name)
    return {"company_name": company_name}


def fetch_company_info_node(state: AgentState) -> dict:
    print("Extracting Company Information")
    company_info, failed  = tools.get_company_info(state['company_name'])
    print("Company Info: ", company_info)
    return {"company_info" : company_info, "company_info_failed" : failed}


def read_cv_node(state:AgentState) -> dict:
    print("Reading CV")
    cv_text = tools.read_cv()
    if not cv_text:
        return {
            "cv_text" : "",
            "status" : "CV_TEXT_FAILED"
        }
    return{"cv_text" : cv_text}



def tailor_cv_node


def draft_cover_letter_node




def save_files_node



def human_approval_node



def send_email_node



def route_after_approval