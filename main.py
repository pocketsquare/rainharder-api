# main.py - Entry point
from api.index import app

# This is where you'd add any startup logic, 
# background tasks, or other orchestration later

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


from api import router as api_router

app.include_router(api_router)
