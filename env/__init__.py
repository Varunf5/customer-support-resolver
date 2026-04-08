"""
Customer Support Ticket Resolver Environment Package.
An OpenEnv-compliant environment for simulating customer support ticket resolution.
"""

from .environment import SupportTicketEnvironment
from .models import (
    Observation,
    Action,
    Ticket,
    Message,
    EnvironmentInfo,
    TaskResult,
    RewardBreakdown,
)
from .tasks import TaskManager
from .grader import grade_environment, grade_task_result, calculate_episode_performance

__all__ = [
    "SupportTicketEnvironment",
    "Observation",
    "Action",
    "Ticket",
    "Message",
    "EnvironmentInfo",
    "TaskResult",
    "RewardBreakdown",
    "TaskManager",
    "grade_environment",
    "grade_task_result",
    "calculate_episode_performance",
]
