from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.router_routes import router as router_routes

app = FastAPI(
    title="AI Assistant API",
    description="Backend for AI-powered phone search and movie lookup agents",
    version="1.0.0"
)

# Allow UI frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(router_routes, prefix="/routes", tags=["AIAssistant"])



@app.get("/")
def root():
    return {
        "message": "AI Assistant API Running",
        "endpoints": {
            "phone": "/phone/search?q=iphone 16",
            "movie": "/movie/search?q=Dunki movie showtimes"
        }
    }
