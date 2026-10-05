# AI Meeting Action-Item Extractor

AI-powered application that converts meeting transcripts into structured action items containing the task, owner, deadline, and confidence.

## Architecture

Streamlit → FastAPI → Controller → Service → Extraction/Validation → Repository → PostgreSQL

The extraction layer supports configurable mock, OpenAI, Groq, and Gemini providers.

## Development

Install the project and run tests with Python 3.13+:

    python -m pip install -e .
    pytest

## Configuration

Set environment variables such as DATABASE_URL, LLM_PROVIDER, LLM_MODEL, OPENAI_API_KEY, GROQ_API_KEY, and GEMINI_API_KEY. See .env.example for the configuration template.

## API

Run the API with:

    uvicorn apps.api.main:app --host 0.0.0.0 --port 8000

The extraction endpoint is POST /api/v1/extract.

## Evaluation

The project includes an annotated dataset and evaluation code for precision, recall, and F1 measurement.

## Deployment

The FastAPI backend can be deployed as a Render Web Service. The repository pins Python 3.13.5 through .python-version for deployment compatibility.
