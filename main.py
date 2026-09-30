import uvicorn

if __name__ == "__main__":
    print("[INFO] Starting Edge Automated Optical Inspection Engine...")
    print("[INFO] Inspection Console: http://127.0.0.1:8000")
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=False, workers=1)
