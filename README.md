# CHAI-chatbot

### Environment Setup
1. Install depedencies 
```
brew install uv docker
uv sync
```
2. Start Up Application And DB
```
./scripts/start_demo.sh
```
3. Go to UI
```
http://localhost:8000/chatbot
```

### Changelog

### [0.2.0]
- Removed
    - Removed internal APIs for now, can be added later for internal debugging purpose

- Added
    - Added PostgreSQL to store user accounts, chatbots, and conversations.
    - Integrated Redis for storing and retrieving chat histories.
    - Added support for concurrent multi-user sessions 
    - UI improvements:
        - Support users registration/login
        - View past conversations.
        - Create and manage multiple chatbots.
    - User and chatbot data now persist across logins and application restarts.