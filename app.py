"""
Flask API for HuggingFace Spaces compatibility.
Provides REST endpoints for environment interaction.

Usage:
  python app.py

Then access:
  - GET /health
  - POST /reset
  - POST /step
  - GET /state
  - POST /inference
"""

import json
import os
import sys
import importlib.util

# Robust import handling for different environments (local, Docker, HuggingFace Spaces)
def import_env_module():
    """Import the env module with fallback strategies."""
    try:
        # Try direct import first
        from env import SupportTicketEnvironment, TaskManager, grade_task_result
        return SupportTicketEnvironment, TaskManager, grade_task_result
    except ImportError:
        try:
            # Try adding current directory to path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            from env import SupportTicketEnvironment, TaskManager, grade_task_result
            return SupportTicketEnvironment, TaskManager, grade_task_result
        except ImportError:
            try:
                # Try importing as a module from file path
                env_path = os.path.join(os.path.dirname(__file__), 'env', '__init__.py')
                spec = importlib.util.spec_from_file_location("env", env_path)
                env_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(env_module)
                return env_module.SupportTicketEnvironment, env_module.TaskManager, env_module.grade_task_result
            except Exception as e:
                raise ImportError(f"Could not import env module: {e}")

# Import the modules
SupportTicketEnvironment, TaskManager, grade_task_result = import_env_module()

from flask import Flask, request, jsonify

app = Flask(__name__)

# Global environment instance (for Spaces compatibility)
env = None

def init_environment():
    """Initialize the environment."""
    global env
    env = SupportTicketEnvironment()
    return env

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Customer Support Ticket Resolver",
        "version": "1.0.0"
    }), 200

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the environment and return initial observation."""
    global env
    if env is None:
        init_environment()

    observation = env.reset()
    return jsonify({
        "observation": observation.model_dump(),
        "message": "Environment reset successfully"
    }), 200

@app.route('/step', methods=['POST'])
def step():
    """Execute one step in the environment."""
    global env
    if env is None:
        init_environment()

    try:
        action_data = request.get_json()
        if not action_data or 'action_type' not in action_data:
            return jsonify({"error": "Missing action_type"}), 400

        from env.models import Action
        action = Action(**action_data)

        observation, reward, done, info = env.step(action)
        return jsonify({
            "observation": observation.model_dump(),
            "reward": float(reward),
            "done": done,
            "info": {
                "step_count": info.step_count,
                "action_type": info.action_type,
                "action_valid": info.action_valid,
                "message": info.message,
                "reward_breakdown": info.reward_breakdown
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/state', methods=['GET'])
def get_state():
    """Get the current environment state."""
    global env
    if env is None:
        init_environment()

    state = env.state()
    if hasattr(state.get('ticket'), 'model_dump'):
        state['ticket'] = state['ticket'].model_dump()

    return jsonify(state), 200

@app.route('/inference', methods=['POST'])
def run_inference():
    """Run full inference for easy, medium, and hard tasks."""
    global env
    if env is None:
        init_environment()

    try:
        def grader_fn(environment):
            return {"score": environment.episode_score}

        task_manager = TaskManager(grader_fn=grader_fn)

        easy_result = task_manager.run_easy_task(env)
        easy_score = grade_task_result("easy", easy_result.score)

        medium_result = task_manager.run_medium_task(env)
        medium_score = grade_task_result("medium", medium_result.score)

        hard_result = task_manager.run_hard_task(env)
        hard_score = grade_task_result("hard", hard_result.score)

        return jsonify({
            "easy_score": float(easy_score),
            "medium_score": float(medium_score),
            "hard_score": float(hard_score),
            "total_score": float((easy_score + medium_score + hard_score) / 3)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/health",
            "/reset",
            "/step",
            "/state",
            "/inference"
        ]
    }), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({"error": str(error)}), 500

if __name__ == '__main__':
    init_environment()
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 7860))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print(f"Starting Customer Support Ticket Resolver API...")
    print(f"Listening on {host}:{port}")
    print(f"Available endpoints:")
    print(f"  - GET  /health")
    print(f"  - POST /reset")
    print(f"  - POST /step")
    print(f"  - GET  /state")
    print(f"  - POST /inference")

    app.run(host=host, port=port, debug=debug, threaded=True)
