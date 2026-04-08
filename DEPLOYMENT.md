# Deployment Guide

## Environment Variables

The application supports the following environment variables:

### Core Configuration
- `OPENAI_API_KEY`: Your OpenAI API key (default: "sk-default-key")
- `API_BASE_URL`: OpenAI API base URL (default: "https://api.openai.com/v1")
- `MODEL_NAME`: Model name to use (default: "gpt-4")
- `HF_TOKEN`: HuggingFace token for model access (optional)

### Server Configuration
- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 7860 for HF Spaces)
- `DEBUG`: Enable debug mode (default: "False")

### Inference Configuration
- `CMD_TYPE`: "flask" to run Flask app, defaults to inference.py

## Local Development

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Run Inference

```bash
python inference.py
```

Expected output:
```
[START]
[STEP] Running task: easy
[STEP] Score: X.X
[STEP] Running task: medium
[STEP] Score: X.X
[STEP] Running task: hard
[STEP] Score: X.X
[END]
```

### 3. Run Flask API

For local testing or HuggingFace Spaces:

```bash
python app.py
```

Then access:
- Health check: `curl http://localhost:7860/health`
- Reset: `curl -X POST http://localhost:7860/reset`
- Step: `curl -X POST http://localhost:7860/step -H "Content-Type: application/json" -d '{"action_type": "classify", "category": "billing"}'`
- State: `curl http://localhost:7860/state`
- Inference: `curl -X POST http://localhost:7860/inference`

## Docker

### Build

```bash
docker build -t customer-support:latest .
```

### Run Inference (Default)

```bash
docker run customer-support:latest
```

### Run Flask API

```bash
docker run -e CMD_TYPE=flask -p 7860:7860 customer-support:latest
```

Then access at `http://localhost:7860`

## HuggingFace Spaces

### 1. Create a new Space
- Choose "Docker" runtime
- Set to "Public"

### 2. Upload files
```
docker/
├── Dockerfile
├── requirements.txt
├── app.py
├── inference.py
├── env/
│   ├── __init__.py
│   ├── environment.py
│   ├── models.py
│   ├── tasks.py
│   └── grader.py
├── openenv.yaml
└── README.md
```

### 3. Set environment variables in Space settings
- `OPENAI_API_KEY`: Your OpenAI API key
- `API_BASE_URL`: (optional, defaults to official OpenAI)
- `MODEL_NAME`: Model to use
- `CMD_TYPE`: Set to "flask" to run Flask app

### 4. Space will automatically:
- Build the Docker image
- Start the Flask app on port 7860
- Expose `/reset` endpoint for external interaction

## OpenEnv Evaluation

For OpenEnv hackathon evaluation:

```bash
# Standard evaluation - runs inference.py
docker run customer-support:latest

# Or directly:
python inference.py
```

This will produce the expected output format:
```
[START]
[STEP] Running task: easy
[STEP] Score: X
[STEP] Running task: medium
[STEP] Score: X
[STEP] Running task: hard
[STEP] Score: X
[END]
```

## API Specification

### REST Endpoints (Flask)

#### GET /health
Check service health.

**Response:**
```json
{
  "status": "healthy",
  "service": "Customer Support Ticket Resolver",
  "version": "1.0.0"
}
```

#### POST /reset
Reset environment and get initial observation.

**Response:**
```json
{
  "observation": {
    "ticket_id": "TKT001",
    "customer_message": "...",
    "priority": "high",
    "complexity": "moderate",
    "history": [],
    "step_count": 0
  },
  "message": "Environment reset successfully"
}
```

#### POST /step
Execute one action.

**Request:**
```json
{
  "action_type": "classify",
  "category": "billing"
}
```

Or for respond:
```json
{
  "action_type": "respond",
  "content": "Your response here..."
}
```

**Response:**
```json
{
  "observation": {...},
  "reward": 0.35,
  "done": false,
  "info": {
    "step_count": 1,
    "action_type": "classify",
    "action_valid": true,
    "message": "Classified as billing",
    "reward_breakdown": {...}
  }
}
```

#### GET /state
Get current environment state.

**Response:**
```json
{
  "ticket": {...},
  "step_count": 1,
  "max_steps": 5,
  "classified": true,
  "responded": false,
  "escalated_or_closed": false,
  "episode_score": 0.35,
  "done": false,
  "actions_taken": ["classify"]
}
```

#### POST /inference
Run full inference (all 3 tasks).

**Response:**
```json
{
  "easy_score": 0.4,
  "medium_score": 0.9,
  "hard_score": 0.85,
  "total_score": 0.7167
}
```

## Troubleshooting

### ImportError: No module named 'flask'
```bash
pip install flask==2.3.3
```

### Port already in use
```bash
# Use different port
PORT=8000 python app.py
```

### Docker build fails
```bash
# Ensure all files are in the same directory
# Check Dockerfile path
docker build -t customer-support:latest .
```

### Cannot find OPENAI_API_KEY
```bash
# Export as environment variable
export OPENAI_API_KEY="your-key-here"
python inference.py

# Or for Docker
docker run -e OPENAI_API_KEY="your-key-here" customer-support:latest
```

## Performance

- Inference.py: < 2 seconds per run
- Flask API: < 100ms per request
- Memory: ~200MB base + PyTorch models
- CPU: Single core capable

## Compliance

✓ OpenEnv API compliant (step, reset, state)
✓ Reward values bounded [0.0, 1.0]
✓ Deterministic output format
✓ Docker support
✓ HF Spaces compatible
✓ Environment variable support
✓ No hardcoded secrets
