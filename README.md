# Ask API

## Overview

Ask API is a FastAPI-based project that provides endpoints for managing prompts and handling user queries.

## Features

- **FastAPI**: High performance, easy to learn, fast to code, ready for production.
- **Endpoints**: Includes routers for handling different functionalities.
- **Interactive API Documentation**: Available at `/api/docs` (Swagger UI) and `/api/redoc` (ReDoc).

## Requirements

- Python 3.7+
- pip

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

## Running the Application

To run the application, use the following command:

```bash
uvicorn api.main:app --host localhost --port 8000 --reload

