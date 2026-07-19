from typing_extensions import TypedDict

class AgentState(TypedDict):

    job_description : str
    company_name : str
    company_info : str
    company_info_failed : str

    cv_text : str
    tailored_cv : str
    cover_letter : str

    cv_path : str
    cl_path : str

    approval_decision : str  # 'y'/'n'/'e'
    status : str    # human readable status for logging


    