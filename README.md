# ITSS PROJECT

### FRONTEND
- Yarn, React, Tailwind
```sh
cd frontend
yarn dev
```

- Install dependencies, using this command:
```sh
yarn add <dependencies> -W
```

### BACKEND
- FastAPI, MongoDB
```sh
cd backend
docker compose up -d
python app/main.py
```
- Fix ImportError: email-validator is not installed, run pip install pydantic[email]
```sh
pip install 'pydantic[email]'
```

- Open: http://127.0.0.1:8000/docs

### DATABASE
- MongoDB WebUI: http://127.0.0.1:8081/
- Credential: root - password
