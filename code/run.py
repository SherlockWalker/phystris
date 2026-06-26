import uvicorn

# Change your socket host here
uvicorn.run("server:app", host="127.0.0.1", port=5000)
