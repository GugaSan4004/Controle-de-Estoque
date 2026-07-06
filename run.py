import sys
import uvicorn

if __name__ == "__main__":
    reload = True if "--debug" in sys.argv else False
    uvicorn.run("server:app", port=5500, log_level="info", reload=reload)