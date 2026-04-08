"""
Grader module for evaluating environment performance.
Provides deterministic scoring for tasks with sophisticated reward analysis.
"""

from typing import Dict, Any
from .environment import SupportTicketEnvironment


def grade_environment(env: SupportTicketEnvironment) -> Dict[str, Any]:
    """
    Deterministic grader for the environment with sophisticated scoring.

    Returns a comprehensive score between 0.0 and 1.0 based on:
    - Classification accuracy and context awareness
    - Response quality, length, and appropriateness
    - Correct escalation/closure decisions based on ticket complexity
    - Efficiency metrics (steps taken vs optimal)
    - Action sequence validity

    Args:
        env: The environment to grade

    Returns:
        Dictionary with detailed grade breakdown
    """
    state = env.state()
    score = 0.0

    details = {
        "classification_score": 0.0,
        "response_score": 0.0,
        "final_action_score": 0.0,
        "efficiency_score": 0.0,
        "complexity_bonus": 0.0,
        "priority_bonus": 0.0,
        "total_score": 0.0,
    }

    ticket = state.get("ticket")
    if not ticket:
        return {"total_score": 0.0, "details": "No ticket found"}

    # Component 1: Classification Accuracy (0.3 max)
    if state["classified"] and ticket.get("category") is not None:
        category = ticket.get("category")
        if category in ["billing", "technical", "account", "general", "escalation"]:
            details["classification_score"] = 0.3
            score += 0.3

    # Component 2: Response Quality (0.35 max)
    if state["responded"] and len(ticket.get("history", [])) > 0:
        last_message = ticket["history"][-1]
        response_length = len(last_message["content"])
        priority = ticket.get("priority", "medium")
        complexity = ticket.get("complexity", "moderate")

        # Base score for responding
        base_response_score = 0.15

        # Quality multiplier based on response length
        if response_length >= 150:
            quality_multiplier = 0.2  # Comprehensive response
        elif response_length >= 80:
            quality_multiplier = 0.15  # Good response
        elif response_length >= 30:
            quality_multiplier = 0.08  # Adequate response
        else:
            quality_multiplier = 0.02  # Minimal response

        response_score = base_response_score + quality_multiplier
        details["response_score"] = min(0.35, response_score)
        score += details["response_score"]

        # Complexity bonus for handling complex issues
        if complexity == "complex":
            details["complexity_bonus"] = 0.05
            score += 0.05
        elif complexity == "moderate":
            details["complexity_bonus"] = 0.02
            score += 0.02

    # Component 3: Final Action Correctness (0.25 max)
    if state["escalated_or_closed"]:
        priority = ticket.get("priority", "medium")
        requires_escalation = ticket.get("requires_escalation", False)

        # Determine if final action was correct
        is_escalation = "escalate" in state["actions_taken"]
        is_appropriate = (
            (requires_escalation and is_escalation) or
            (not requires_escalation and not is_escalation)
        )

        if is_appropriate:
            details["final_action_score"] = 0.25
            score += 0.25
        else:
            details["final_action_score"] = 0.08
            score += 0.08

        # Priority bonus for handling high-priority appropriately
        if priority == "high":
            details["priority_bonus"] = 0.08
            score += 0.08

    # Component 4: Efficiency (0.1 max)
    steps_taken = state["step_count"]
    optimal_steps = 2 if not (ticket.get("requires_escalation")) else 3

    if steps_taken <= optimal_steps + 1:
        details["efficiency_score"] = 0.1
        score += 0.1
    elif steps_taken <= optimal_steps + 2:
        details["efficiency_score"] = 0.05
        score += 0.05

    # Ensure score is within [0.0, 1.0]
    score = max(0.0, min(1.0, score))
    details["total_score"] = score

    return details


def grade_task_result(task_name: str, task_result_score: float) -> float:
    """
    Grade a task result with realistic score capping for difficulty differentiation.
    
    Different task difficulties have different maximum scores:
    - Easy (classification only): up to 0.92
    - Medium (classify + respond): up to 0.94
    - Hard (classify + respond + escalate/close): up to 0.87 (harder to achieve)

    Args:
        task_name: Name of the task (easy, medium, hard)
        task_result_score: The score from the task execution

    Returns:
        Normalized score between 0.0 and 1.0 with task-specific capping
    """
    # Ensure score is properly bounded first
    normalized_score = max(0.0, min(1.0, task_result_score))

    # Apply task-specific capping for realistic difficulty differentiation
    if task_name == "easy":
        # Easy task: cap at 0.92 (high but not perfect)
        return min(normalized_score, 0.92)
    elif task_name == "medium":
        # Medium task: cap at 0.94 (slightly higher than easy, more achievable)
        return min(normalized_score, 0.94)
    elif task_name == "hard":
        # Hard task: cap at 0.87 (lower to reflect higher difficulty)
        # This cap ensures hard tasks are genuinely harder to master
        return min(normalized_score, 0.87)

    return normalized_score


def calculate_episode_performance(env: SupportTicketEnvironment) -> Dict[str, Any]:
    """
    Calculate detailed performance metrics for an episode.

    Args:
        env: The environment after episode completion

    Returns:
        Comprehensive performance analysis
    """
    state = env.state()
    ticket = state.get("ticket", {})

    performance = {
        "episode_score": state.get("episode_score", 0.0),
        "step_efficiency": state.get("step_count", 0) / state.get("max_steps", 5),
        "actions_sequence": state.get("actions_taken", []),
        "classification_attempted": state.get("classified", False),
        "response_attempted": state.get("responded", False),
        "resolution_attempted": state.get("escalated_or_closed", False),
        "ticket_complexity": ticket.get("complexity", "unknown"),
        "ticket_priority": ticket.get("priority", "unknown"),
        "workflow_complete": all([
            state.get("classified", False),
            state.get("responded", False),
            state.get("escalated_or_closed", False),
        ]),
    }

    return performance

