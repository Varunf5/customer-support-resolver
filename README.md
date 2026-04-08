---
title: Customer Support Ticket Resolver Environment
emoji: 📩
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "latest"
app_file: app.py
pinned: false
---

# Customer Support Ticket Resolver Environment

A production-ready OpenEnv-compliant environment for simulating customer support ticket resolution using AI agents.

## Project Overview

This project implements a real-world simulation of a customer support system where an AI agent resolves support tickets through a series of structured actions. The environment follows the OpenEnv API standard with `step()`, `reset()`, and `state()` methods.

### Real-World Motivation

Modern customer support teams handle thousands of tickets daily across multiple categories (billing, technical, account management). Automating ticket resolution through intelligent agents can:
- **Reduce response time** for simple and moderate issues
- **Classify tickets accurately** for proper routing and prioritization
- **Escalate complex issues** to specialists while handling simple ones independently
- **Improve customer satisfaction** with consistent, helpful responses tailored to issue severity
- **Allow human agents** to focus on high-value and complex interactions
- **Track metrics** like resolution time, escalation rate, and customer satisfaction

This environment simulates these real-world challenges with:
- **12 diverse ticket scenarios** covering billing, technical, account, and general issues
- **Context-aware reward mechanisms** that account for ticket complexity and priority
- **Realistic escalation rules** based on issue severity and type
- **Dynamic response evaluation** based on response quality and length

## Project Structure

```
customer-support-env/
├── env/
│   ├── __init__.py
│   ├── environment.py      # Core OpenEnv implementation
│   ├── models.py           # Pydantic data models
│   ├── tasks.py            # Task definitions (easy, medium, hard)
│   └── grader.py           # Deterministic graders
│
├── inference.py            # Agent interaction and evaluation script
├── openenv.yaml            # OpenEnv specification
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## OpenEnv API Specification

The environment implements three core methods as per OpenEnv standard:

### `reset() → Observation`
Resets the environment and returns the initial observation for a new episode.

**Returns:**
- `Observation`: Initial ticket information
  - `ticket_id`: Unique identifier
  - `customer_message`: Initial customer message
  - `priority`: Ticket priority (low/medium/high)
  - `complexity`: Issue complexity (simple/moderate/complex)
  - `history`: Empty conversation history
  - `step_count`: 0

### `step(action: Action) → (Observation, float, bool, EnvironmentInfo)`
Execute one step in the environment.

**Parameters:**
- `action`: Action object with:
  - `action_type`: One of ["classify", "respond", "escalate", "close"]
  - `content`: Optional response text
  - `category`: Optional category (for classify action)

**Returns:**
- `observation`: Updated ticket observation
- `reward`: Float between 0.0 and 1.0 (context-aware)
- `done`: Boolean indicating episode termination
- `info`: Additional step information including reward breakdown

### `state() → Dict[str, Any]`
Get the current complete environment state.

**Returns:**
- Dictionary containing:
  - `ticket`: Full ticket data with complexity and escalation info
  - `step_count`: Current step number
  - `done`: Episode status
  - `episode_score`: Total accumulated reward
  - `actions_taken`: List of actions taken
  - `classified`: Whether classified
  - `responded`: Whether responded
  - `escalated_or_closed`: Whether terminal action taken

## Observation Space

Each observation contains ticket information:

```python
{
    "ticket_id": str,              # e.g., "TKT001"
    "customer_message": str,       # Initial customer message
    "priority": str,               # "low" | "medium" | "high"
    "complexity": str,             # "simple" | "moderate" | "complex"
    "history": List[Message],      # Conversation history
    "step_count": int              # Current step (0-5)
}
```

### Message Format
```python
{
    "role": str,     # "customer" | "agent"
    "content": str,  # Message text
    "timestamp": str # Optional timestamp
}
```

## Action Space

Agents can take the following actions:

### 1. Classify Action
```python
{
    "action_type": "classify",
    "category": str  # One of: ["billing", "technical", "account", "general", "escalation"]
}
```
**Base Reward:** 0.25

**Modifiers:**
- Priority bonus (HIGH: +0.08, MEDIUM: +0.04)
- Complexity bonus (COMPLEX: +0.06, MODERATE: +0.03)

### 2. Respond Action
```python
{
    "action_type": "respond",
    "content": str  # Response text (minimum 15 characters)
}
```
**Base Reward:** 0.30

**Quality Bonus:**
- 150+ characters: +0.25 (comprehensive)
- 80-149 characters: +0.15 (good)
- 30-79 characters: +0.08 (adequate)
- <30 characters: +0.02 (minimal)

**Additional Modifiers:**
- Priority bonus (HIGH: +0.08, MEDIUM: +0.03)
- Complexity bonus (COMPLEX: +0.07, MODERATE: +0.03)

### 3. Escalate Action
```python
{
    "action_type": "escalate"
}
```
**Base Reward:** 0.15

**Decision Bonus:**
- Correct escalation (complex/high-priority): +0.15
- Unnecessary escalation: -0.10

**Effect:** Immediately terminates episode

### 4. Close Action
```python
{
    "action_type": "close"
}
```
**Base Reward:** 0.15

**Decision Bonus:**
- Correct closure (simple/low-priority): +0.15
- Premature closure: -0.08

**Response Quality Bonus:** +0.08 if response was comprehensive

**Effect:** Immediately terminates episode
**Constraint:** Cannot close without responding first

## Advanced Reward Function

The environment uses a sophisticated, context-aware reward system:

### Reward Components

1. **Base Reward**: Core points for taking an action
2. **Priority Bonus**: Higher priority tickets reward more
3. **Complexity Bonus**: Complex issues reward correct handling more
4. **Quality Bonus**: Response quality directly affects rewards
5. **Efficiency Penalty**: Exceeding step limits penalizes
6. **Repetition Penalty**: Repeated actions are discouraged

### Reward Calculation Example

```
Classify high-priority complex ticket:
  Base: 0.25 + Priority: 0.08 + Complexity: 0.06 = 0.39

Respond with 120-character message to complex issue:
  Base: 0.30 + Quality: 0.15 + Priority: 0.08 + Complexity: 0.07 = 0.60

Correctly escalate complex high-priority issue:
  Base: 0.15 + Correct decision: 0.15 + Priority: 0.08 = 0.38

Total episode reward: Up to 1.0 (clipped)
```

## Sample Tickets (12 Diverse Scenarios)

The environment includes 12 realistic tickets:

### Billing Issues (TKT001-TKT003)
- **TKT001**: Double charge - HIGH priority, MODERATE complexity, requires escalation
- **TKT002**: Unresolved cancellation - HIGH priority, COMPLEX, requires escalation  
- **TKT003**: Refund policy question - LOW priority, SIMPLE

### Technical Issues (TKT004-TKT006)
- **TKT004**: Upload failure - HIGH priority, COMPLEX, requires escalation
- **TKT005**: Error 503 - HIGH priority, COMPLEX, requires escalation
- **TKT006**: 2FA setup - LOW priority, SIMPLE

### Account Issues (TKT007-TKT009)
- **TKT007**: Login failure - HIGH priority, MODERATE, requires escalation
- **TKT008**: Profile update - LOW priority, SIMPLE
- **TKT009**: Security breach - HIGH priority, COMPLEX, requires escalation

### General/Product Questions (TKT010-TKT012)
- **TKT010**: Plan comparison - LOW priority, SIMPLE
- **TKT011**: Data export - MEDIUM priority, MODERATE
- **TKT012**: Export broken - HIGH priority, COMPLEX, requires escalation

## Task Definitions

### EASY Task: Ticket Classification
**Goal:** Classify the support ticket correctly.

**Evaluation:**
- Single action: classify
- Valid category selection
- Reward: varies by priority/complexity

**Expected score range:** 0.25-0.39 (depends on ticket attributes)

### MEDIUM Task: Classification + Response
**Goal:** Classify ticket and provide a helpful, contextually appropriate response.

**Evaluation:**
- Two actions: classify → respond
- Correct classification based on ticket keywords
- Response quality based on length and relevance
- Contextual appropriateness for ticket type/priority

**Expected score range:** 0.50-0.99 (0.25-0.39 + 0.25-0.60)

### HARD Task: Full Resolution
**Goal:** Complete ticket resolution through classify → respond → escalate/close with correct decision-making.

**Evaluation:**
- Three actions: classify → respond → escalate/close
- Correct classification
- Quality response (50+ chars for simple, 80+ for complex)
- Correct escalation/closure decision:
  - complex/high-priority/requires_escalation → escalate
  - simple/low-priority/not requires_escalation → close
- Efficient resolution (optimal steps = 2-3)

**Expected score range:** 0.68-1.0+ (0.25-0.39 + 0.25-0.60 + 0.15-0.38)

## Grading System

The environment provides sophisticated, deterministic grading:

```python
grade_environment(env) → Dict[str, float]
```

**Scoring Components:**
- **Classification accuracy:** 0.0-0.3 (correct category match)
- **Response quality:** 0.0-0.35 (length, relevance, appropriateness)
- **Complexity handling:** 0.0-0.15 (bonus for complex issues)
- **Priority handling:** 0.0-0.15 (bonus for high-priority)
- **Final action correctness:** 0.0-0.25 (escalate vs close decision)
- **Efficiency:** 0.0-0.1 (steps taken vs optimal)

**Total score:** 0.0-1.0

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip package manager
- Optional: Docker for containerized deployment

### Local Installation

1. **Clone/navigate to the project:**
   ```bash
   cd customer-support-env
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables (optional):**
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   export API_BASE_URL=https://api.openai.com/v1
   export MODEL_NAME=gpt-4
   ```

### Docker Setup

1. **Build the Docker image:**
   ```bash
   docker build -t customer-support-env:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -e OPENAI_API_KEY=sk-your-key-here customer-support-env:latest
   ```

## Running the Project

### Run Inference Script Locally

```bash
python inference.py
```

This executes all three tasks (easy, medium, hard) and produces evaluation logs.

### Run Specific Tasks

Create a test script to run individual tasks:

```python
from env import SupportTicketEnvironment, TaskManager, grade_task_result

env = SupportTicketEnvironment()
task_manager = TaskManager(grader_fn=lambda e: {})

# Run easy task
result = task_manager.run_easy_task(env)
print(f"Easy task score: {result.score:.2f}")

# Run medium task
result = task_manager.run_medium_task(env)
print(f"Medium task score: {result.score:.2f}")

# Run hard task
result = task_manager.run_hard_task(env)
print(f"Hard task score: {result.score:.2f}")
```

### Inspect Environment State

```python
from env import SupportTicketEnvironment, Action

env = SupportTicketEnvironment()
obs = env.reset()

print(f"Ticket: {obs.ticket_id}")
print(f"Priority: {obs.priority}")
print(f"Complexity: {obs.complexity}")
print(f"Message: {obs.customer_message[:50]}...")

# Take an action
action = Action(action_type="classify", category="technical")
next_obs, reward, done, info = env.step(action)

print(f"Reward: {reward:.2f}")
print(f"Breakdown: {info.reward_breakdown}")
print(f"Done: {done}")

# Inspect full state
state = env.state()
print(f"Episode score: {state['episode_score']:.2f}")
```

## Expected Output

When running `inference.py`, the output follows this exact format:

```
[START]
[STEP] Running task: easy
[STEP] Score: 0.3
[STEP] Running task: medium
[STEP] Score: 0.7
[STEP] Running task: hard
[STEP] Score: 0.9
[END]
```

**Note:** Exact scores will vary based on:
- Random ticket selection (12 different scenarios)
- Ticket complexity and priority attributes
- Context-aware reward calculations
- Specific escalation requirements per ticket

Typical score ranges:
- Easy: 0.25-0.39
- Medium: 0.50-0.99
- Hard: 0.68-1.0

## Code Quality

This project includes:

✅ **Type hints** throughout using Python type annotations
✅ **Pydantic models** for data validation and schema
✅ **OpenEnv-compliant API** with step(), reset(), state()
✅ **Context-aware reward system** with detailed breakdowns
✅ **Deterministic grading** for objective evaluation
✅ **12 diverse ticket scenarios** covering real support cases
✅ **Clean code structure** with separation of concerns
✅ **Comprehensive docstrings** for all classes and methods
✅ **Error handling** for invalid actions and edge cases
✅ **Production-ready** with no placeholders or TODOs

## Improvements Made

Recent enhancements include:

### Reward Function
- Context-aware rewards based on ticket priority and complexity
- Quality-based bonuses for response length and comprehensiveness
- Correct escalation decision detection and rewards
- Detailed reward breakdown reporting per step

### Ticket Library
- Expanded from 5 to 12 diverse, realistic scenarios
- Clear complexity levels for each ticket
- Proper escalation requirements defined per ticket
- More realistic customer messages and support scenarios
- Categorization across 4 domains: billing, technical, account, general

### Task Improvements
- Better evaluation metrics for each task level
- Response quality assessment based on multiple factors
- Complexity-aware task difficulty progression
- More detailed task execution reporting

### Grading System
- Multi-component scoring methodology
- Priority and complexity handling bonuses
- Efficiency scoring based on step counts
- Comprehensive performance metrics reporting

## Extensions and Customization

### Adding New Sample Tickets

Edit `env/environment.py` and add to `SAMPLE_TICKETS`:

```python
{
    "ticket_id": "TKT006",
    "customer_message": "Your message here",
    "priority": "high",
    "category": None,
}
```

### Adding New Categories

Extend `VALID_CATEGORIES` in `env/environment.py`:

```python
VALID_CATEGORIES = ["billing", "technical", "account", "general", "escalation", "new_category"]
```

### Custom Reward Function

Modify the reward logic in `env/environment.py` `step()` method to implement custom reward schemes.

## Testing

The environment automatically validates:
- Action validity (unknown action types)
- Action parameters (response length, valid categories)
- Episode constraints (max steps, terminal states)
- Reward bounds (always 0.0-1.0)

## Performance Benchmarks

Expected performance on the three tasks:

| Task | Min Score | Expected | Max Score |
|------|-----------|----------|-----------|
| Easy | 0.0 | 0.3 | 0.3 |
| Medium | 0.0 | 0.7 | 0.7 |
| Hard | 0.0 | 0.9 | 1.0 |

## Troubleshooting

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Environment Variable Issues
If OPENAI_API_KEY is not set, a default key is used. Set it explicitly:
```bash
export OPENAI_API_KEY=sk-your-actual-key
```

### Script Not Running
Ensure you're in the correct directory and Python path includes the project root:
```bash
cd customer-support-env
python inference.py
```

## License

This project is provided as-is for evaluation and educational purposes.

## Contact

For issues or questions about this environment, refer to the code documentation and docstrings for detailed API information.
