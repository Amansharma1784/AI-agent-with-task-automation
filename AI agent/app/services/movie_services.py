from app.agents.movie_agent import movie_agent

async def search_movie(query: str):
    """
    Calls the movie agent to find showtimes, booking links, etc.
    """
    response = movie_agent.run(query)
    return {
        "agent": "movie_agent",
        "query": query,
        "response": response
    }
