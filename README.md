# Accompany
A fully opensource ERP software


## To run the project:

### 1. Create a python virtual environment:
```bash
python -m venv venv
```

### 2. Activate the virtual environment:
```bash
source venv/bin/activate
```

### 3. Install the required dependencies:
```bash
pip install -r app/requirements.txt
```

### 4. To run the server:
```bash
uvicorn app.main:app --reload
```