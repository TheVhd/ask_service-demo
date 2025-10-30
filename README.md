# 🧠 ASK Service  
### Conversational AI API for Educational RAG Systems  

_“Before agents, there was ASK — the seed of conversational learning intelligence.”_

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG%20Pipeline-orange)](https://www.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🧩 Overview  

ASK Service was an early backend API prototype that enabled **students to chat with their textbooks** using LLM-powered retrieval and reasoning.  
It powered the initial **Learning Matrix (LMXAI)** architecture by connecting document parsing, vector storage, and question-answering in a single endpoint.  

---

## ⚙️ Core Features  


✅ FastAPI REST interface with async support  
✅ Persistent chat logging with MongoDB  

---

## 🧠 Architecture  

| Component | Description |
|------------|-------------|
| **AskEndpoint** | Answers Users Question with pedagogical disciplines |
| **Memory** | Persistent Memory with mongoDb|
| **Logs** | Persists queries for later analysis |

---

## 🚀 Quick Start  

```bash
# 1. Clone repository
git clone https://github.com/TheVhd/ask-service.git
cd ask-service

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run locally
uvicorn app.main:app --reload


### Example curl

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "Explain the process of photosynthesis", "document_id": "biology_textbook"}'
```

---

## 🧩 Tech Stack

|Layer|Tools|
|---|---|
|API|FastAPI|
|AI Orchestration|LangChain|
|Database|MongoDB|
|Deployment|Docker / Uvicorn|

---

## 🧾 Demo Purpose

> 🧭 This project is now **archived** and kept public as a **demo reference**  
> for developers exploring **educational AI architectures** and  
> conversational AI backends.

---

## 🌍 Related Projects

|Project|Description|
|---|---|
|[Learning Matrix (LMXAI)](https://lmxai.com/)|AI assistant for personalized learning|
|[Savion](https://savion.app/)|AI diet & clinic assistant|
|[Scraib](https://scraib.ai/)|Voice-to-notes medical assistant|

---

## 🪪 License

MIT License © 2025 [Vahit Uzunlar](https://www.linkedin.com/in/vuzunlar/)

---

# 📡 Ask API

## Overview

Ask API is a FastAPI-based project that provides endpoints for managing prompts and handling user queries.

---

## Features

- **FastAPI**: High performance, easy to learn, fast to code, ready for production.
    
- **Endpoints**: Includes routers for handling different functionalities.
    
- **Interactive API Documentation**: Available at `/api/docs` (Swagger UI) and `/api/redoc` (ReDoc).
    

---

## Requirements

- Python 3.7+
    
- pip
    

---

## Installation

1. Clone the repository:
    
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
    
2. Create a virtual environment and activate it:
    
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
    
3. Install the dependencies:
    
    ```bash
    pip install -r requirements.txt
    ```
    

---

## Running the Application

To run the application, use the following command:

```bash
uvicorn api.main:app --host localhost --port 8000 --reload
```
