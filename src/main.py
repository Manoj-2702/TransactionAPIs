import uvicorn

if __name__ == "__main__":
   print("Server is running!")
   uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
