from agno.team import Team
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from .phone_agent import phone_agent
from .movie_agent import movie_agent
import os
from dotenv import load_dotenv
load_dotenv()



router_agent = Team(
    members=[phone_agent, movie_agent],
    instructions="""
    Your job is to route the user's request to the correct agent.
    
    If the query contains words related to:
    - phone, mobile, price, buy, compare → Use Phone Agent
    - movie, showtime, ticket, cinema → Use Movie Agent

    If uncertain, choose the most relevant match.
    Respond ONLY with the selected agent's output.
    """,
    model=OpenAIChat(id="gpt-4.1-mini",api_key=os.getenv("OPENAI_API_KEY")),
)
