# CHAI-chatbot

### Environment Setup
1. Install depedencies 
```
- brew install uv
- uv sync
```
2. Start Up Application
```
- uvicorn app.main:app --reload
```
3. Go to UI
```
http://localhost:8000/chatbot
```


removed api for now we can added if necessary for internal debugging purpose



postgre with async connection + pool
add search feature

history truncate

chatbot like recommendation
roll back last msg
output two responses for choice