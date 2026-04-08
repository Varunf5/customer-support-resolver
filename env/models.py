"""
Pydantic models for the Customer Support Ticket Resolver Environment.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in the conversation history."""
    role: Literal["customer", "agent"]
    content: str
    timestamp: Optional[str] = None


class Ticket(BaseModel):
    """Represents a customer support ticket."""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    customer_message: str = Field(..., description="Initial message from customer")
    priority: Literal["low", "medium", "high"] = Field(
        default="medium", description="Ticket priority level"
    )
    category: Optional[str] = Field(
        default=None, description="Ticket category (billing, technical, account, etc.)"
    )
    history: List[Message] = Field(default_factory=list, description="Conversation history")
    complexity: Literal["simple", "moderate", "complex"] = Field(
        default="moderate", description="Estimated complexity of the issue"
    )
    expected_resolution: str = Field(
        default="", description="Expected resolution approach"
    )
    requires_escalation: bool = Field(
        default=False, description="Whether issue requires specialist escalation"
    )
    # TOP 5% QUALITY: Metadata for context-aware responses
    customer_sentiment: Literal["angry", "frustrated", "neutral", "satisfied"] = Field(
        default="neutral", description="Customer's emotional state detected from message"
    )
    sla_urgency: Literal["critical", "high", "medium", "low"] = Field(
        default="medium", description="SLA response urgency"
    )
    is_returning_customer: bool = Field(
        default=True, description="Whether this is a returning customer"
    )
    previous_issues_count: int = Field(
        default=0, description="Number of previous support tickets from this customer"
    )


class Observation(BaseModel):
    """Observation returned by the environment."""
    ticket_id: str
    customer_message: str
    priority: Literal["low", "medium", "high"]
    history: List[Message]
    step_count: int = 0
    complexity: Literal["simple", "moderate", "complex"] = "moderate"


class Action(BaseModel):
    """Action taken by the agent."""
    action_type: Literal["classify", "respond", "escalate", "close"]
    content: Optional[str] = Field(default=None, description="Text response for respond action")
    category: Optional[str] = Field(default=None, description="Category for classify action")


class EnvironmentInfo(BaseModel):
    """Information about the step."""
    step_count: int
    action_type: str
    action_valid: bool
    message: Optional[str] = None
    reward_breakdown: Optional[dict] = None


class TaskResult(BaseModel):
    """Result of a task execution."""
    task_name: str
    score: float
    details: Optional[dict] = None


class RewardBreakdown(BaseModel):
    """Detailed breakdown of reward calculation."""
    base_reward: float = 0.0
    priority_bonus: float = 0.0
    complexity_bonus: float = 0.0
    quality_bonus: float = 0.0
    efficiency_penalty: float = 0.0
    repetition_penalty: float = 0.0
    total_reward: float = 0.0
