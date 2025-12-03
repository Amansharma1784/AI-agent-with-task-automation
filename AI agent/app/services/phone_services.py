from app.agents.phone_agent import phone_agent

async def search_phone(query: str):
    print("++++++++++++",query)
    """
    Calls the phone agent with the user query
    and returns structured response with links and pricing.
    """
    response = phone_agent.run(query)
    return {
        "agent": "phone_agent",
        "query": query,
        "response": response
    }
