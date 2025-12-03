from fastapi import APIRouter, Query
from app.agents.router_agent import router_agent  # Team agent

router = APIRouter()






@router.post("/search")
async def router_search(q: str = Query(..., description="Search anything: movie or phone")):
    print("----------------",q)
    
    """
    This endpoint automatically decides whether to call the phone agent
    or movie agent using the router_agent (Team logic).
    """
    data= await router_agent.arun(q)
    # clean_text = data.o["content"]
    all_content = "\n\n".join([res.content for res in data.member_responses])
    print(all_content)

    return all_content
    

