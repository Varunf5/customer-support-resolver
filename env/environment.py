"""
Customer Support Ticket Resolver Environment.
Implements OpenEnv-style API: step(action), reset(), state()
"""

from typing import Tuple, Dict, Any, Optional
import random
from .models import Observation, Action, Ticket, Message, EnvironmentInfo, RewardBreakdown


class SupportTicketEnvironment:
    """
    OpenEnv-compliant environment for customer support ticket resolution.
    """

    # Comprehensive sample tickets with realistic scenarios
    SAMPLE_TICKETS = [
        # BILLING ISSUES
        {
            "ticket_id": "TKT001",
            "customer_message": "I was charged twice for my subscription this month. I'm not sure why this happened and I need this resolved immediately.",
            "priority": "high",
            "complexity": "moderate",
            "category": None,
            "expected_resolution": "Billing refund and account review",
            "requires_escalation": False,
            "customer_sentiment": "frustrated",
            "sla_urgency": "high",
            "is_returning_customer": True,
            "previous_issues_count": 1,
        },
        {
            "ticket_id": "TKT002",
            "customer_message": "Why am I being charged for a service I canceled 3 months ago?",
            "priority": "high",
            "complexity": "complex",
            "category": None,
            "expected_resolution": "Cancel subscription and process refund",
            "requires_escalation": True,
            "customer_sentiment": "angry",
            "sla_urgency": "critical",
            "is_returning_customer": True,
            "previous_issues_count": 2,
        },
        {
            "ticket_id": "TKT003",
            "customer_message": "Quick question: what's your refund policy?",
            "priority": "low",
            "complexity": "simple",
            "category": None,
            "expected_resolution": "Provide policy information",
            "requires_escalation": False,
            "customer_sentiment": "neutral",
            "sla_urgency": "low",
            "is_returning_customer": False,
            "previous_issues_count": 0,
        },
        # TECHNICAL ISSUES
        {
            "ticket_id": "TKT004",
            "customer_message": "The app crashes when I try to upload a file larger than 100MB. This is blocking my work.",
            "priority": "high",
            "complexity": "complex",
            "category": None,
            "expected_resolution": "Technical investigation and fix",
            "requires_escalation": True,
            "customer_sentiment": "frustrated",
            "sla_urgency": "critical",
            "is_returning_customer": True,
            "previous_issues_count": 0,
        },
        {
            "ticket_id": "TKT005",
            "customer_message": "How do I reset my password?",
            "priority": "low",
            "complexity": "simple",
            "category": None,
            "expected_resolution": "Provide password reset instructions",
            "requires_escalation": False,
            "customer_sentiment": "neutral",
            "sla_urgency": "low",
            "is_returning_customer": False,
            "previous_issues_count": 0,
        },
        {
            "ticket_id": "TKT006",
            "customer_message": "I'm getting a 500 error whenever I try to access my dashboard. Other features work fine.",
            "priority": "high",
            "complexity": "complex",
            "category": None,
            "expected_resolution": "Debug backend issue and restore access",
            "requires_escalation": True,
            "customer_sentiment": "frustrated",
            "sla_urgency": "critical",
            "is_returning_customer": True,
            "previous_issues_count": 3,
        },
        # ACCOUNT ISSUES
        {
            "ticket_id": "TKT007",
            "customer_message": "I want to upgrade my account to include more team members.",
            "priority": "medium",
            "complexity": "moderate",
            "category": None,
            "expected_resolution": "Upgrade plan and add users",
            "requires_escalation": False,
            "customer_sentiment": "neutral",
            "sla_urgency": "medium",
            "is_returning_customer": True,
            "previous_issues_count": 5,
        },
        {
            "ticket_id": "TKT008",
            "customer_message": "My account was locked due to suspicious activity. I'm locked out and can't access my data.",
            "priority": "high",
            "complexity": "complex",
            "category": None,
            "expected_resolution": "Verify identity and unlock account",
            "requires_escalation": True,
            "customer_sentiment": "angry",
            "sla_urgency": "critical",
            "is_returning_customer": True,
            "previous_issues_count": 0,
        },
        {
            "ticket_id": "TKT009",
            "customer_message": "Can you help me transfer my account to a new email address?",
            "priority": "medium",
            "complexity": "moderate",
            "category": None,
            "expected_resolution": "Update account email",
            "requires_escalation": False,
            "customer_sentiment": "neutral",
            "sla_urgency": "medium",
            "is_returning_customer": True,
            "previous_issues_count": 2,
        },
        # GENERAL INQUIRIES
        {
            "ticket_id": "TKT010",
            "customer_message": "What are your business hours and how do I contact support?",
            "priority": "low",
            "complexity": "simple",
            "category": None,
            "expected_resolution": "Provide contact information",
            "requires_escalation": False,
            "customer_sentiment": "neutral",
            "sla_urgency": "low",
            "is_returning_customer": False,
            "previous_issues_count": 0,
        },
        {
            "ticket_id": "TKT011",
            "customer_message": "I'm considering switching to your platform but have concerns about data security. Can you address this?",
            "priority": "medium",
            "complexity": "complex",
            "category": None,
            "expected_resolution": "Educational response about security",
            "requires_escalation": True,
            "customer_sentiment": "neutral",
            "sla_urgency": "high",
            "is_returning_customer": False,
            "previous_issues_count": 0,
        },
        {
            "ticket_id": "TKT012",
            "customer_message": "Your product has been great! I want to leave a testimonial.",
            "priority": "low",
            "complexity": "simple",
            "category": None,
            "expected_resolution": "Thank customer and direct to review platform",
            "requires_escalation": False,
            "customer_sentiment": "satisfied",
            "sla_urgency": "low",
            "is_returning_customer": True,
            "previous_issues_count": 6,
        },
    ]

    VALID_CATEGORIES = ["billing", "technical", "account", "general"]
    CATEGORY_MAPPING = {
        "billing": ["charged", "charge", "payment", "invoice", "refund", "subscription", "price", "cost"],
        "technical": ["crash", "error", "bug", "broken", "not working", "slow", "500 error", "dashboard", "upload"],
        "account": ["account", "password", "reset", "email", "locked", "upgrade", "team", "access"],
        "general": ["business hours", "contact", "support", "testimonial", "security", "policy", "about"],
    }

    def __init__(self):
        """Initialize the environment."""
        self.current_ticket = None
        self.step_count = 0
        self.max_steps = 5
        self.classified = False
        self.responded = False
        self.escalated_or_closed = False
        self.episode_score = 0.0
        self.done = False
        self.response_quality = 0.0
        self.actions_taken = []
        self.ticket_history = []
        self.action_sequence = []  # Track action sequence for repeated action penalties

    def reset(self) -> Observation:
        """
        Reset the environment to a fresh state with a new random ticket.
        Returns the initial observation.
        """
        self.current_ticket = Ticket(
            **random.choice(self.SAMPLE_TICKETS)
        )
        self.step_count = 0
        self.classified = False
        self.responded = False
        self.escalated_or_closed = False
        self.episode_score = 0.0
        self.done = False
        self.response_quality = 0.0
        self.actions_taken = []
        self.action_sequence = []  # Reset action tracking
        self.ticket_history.append({
            "ticket_id": self.current_ticket.ticket_id,
            "priority": self.current_ticket.priority,
        })
        return self._get_observation()

    def _get_observation(self) -> Observation:
        """Get current observation."""
        return Observation(
            ticket_id=self.current_ticket.ticket_id,
            customer_message=self.current_ticket.customer_message,
            priority=self.current_ticket.priority,
            history=self.current_ticket.history,
            complexity=self.current_ticket.complexity,
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, EnvironmentInfo]:
        """
        Execute one step in the environment.
        
        Args:
            action: The action to take
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        self.step_count += 1
        self.actions_taken.append(action.action_type)
        self.action_sequence.append(action.action_type)  # Track for repetition detection
        reward = 0.0
        action_valid = True
        message = ""
        reward_breakdown = RewardBreakdown()

        if action.action_type == "classify":
            reward, details = self._calculate_classify_reward(action, reward_breakdown)
            action_valid = details.get("valid", True)
            message = details.get("message", "")
            self.classified = True

        elif action.action_type == "respond":
            reward, details = self._calculate_respond_reward(
                action, reward_breakdown
            )
            action_valid = details.get("valid", True)
            message = details.get("message", "")

        elif action.action_type == "escalate":
            reward, details = self._calculate_escalate_reward(reward_breakdown)
            action_valid = details.get("valid", True)
            message = details.get("message", "")

        elif action.action_type == "close":
            reward, details = self._calculate_close_reward(reward_breakdown)
            action_valid = details.get("valid", True)
            message = details.get("message", "")

        else:
            action_valid = False
            reward = -0.1
            message = f"Unknown action type: {action.action_type}"

        # PENALTY: Repeated actions (e.g., classify twice) indicate poor strategy
        if len(self.action_sequence) >= 2 and self.action_sequence[-1] == self.action_sequence[-2]:
            reward_breakdown.repetition_penalty = -0.15
            reward -= 0.15
            message += " | Repeated action penalty"

        # Step penalty for efficiency
        if self.step_count > 3:
            # Penalty for taking longer than needed
            reward_breakdown.efficiency_penalty = -0.02
            reward -= 0.02
            self.done = True
            message += " (Max steps exceeded)"
        elif self.step_count > 4:
            # Slight penalty for approaching max steps
            reward_breakdown.efficiency_penalty = -0.05

        # Ensure reward is within [0.0, 1.0]
        total_reward = max(0.0, min(1.0, reward))
        reward_breakdown.total_reward = total_reward

        self.episode_score += total_reward

        info = EnvironmentInfo(
            step_count=self.step_count,
            action_type=action.action_type,
            action_valid=action_valid,
            message=message,
            reward_breakdown=reward_breakdown.model_dump(),
        )

        observation = self._get_observation()

        return observation, total_reward, self.done, info

    def _calculate_classify_reward(self, action: Action, breakdown: RewardBreakdown) -> Tuple[float, dict]:
        """Calculate reward for classify action with context awareness."""
        if action.category not in self.VALID_CATEGORIES:
            return 0.0, {
                "valid": False,
                "message": f"Invalid category. Valid: {self.VALID_CATEGORIES}",
            }

        breakdown.base_reward = 0.25

        # Priority bonus: higher priority issues get rewarded more for quick classification
        if self.current_ticket.priority == "high":
            breakdown.priority_bonus = 0.08
        elif self.current_ticket.priority == "medium":
            breakdown.priority_bonus = 0.04

        # SLA urgency bonus: critical/high SLA gets extra reward for quick classification
        if self.current_ticket.sla_urgency == "critical":
            breakdown.priority_bonus += 0.05
        elif self.current_ticket.sla_urgency == "high":
            breakdown.priority_bonus += 0.03

        # Complexity bonus: resolving complex issues is rewarded more
        if self.current_ticket.complexity == "complex":
            breakdown.complexity_bonus = 0.06
        elif self.current_ticket.complexity == "moderate":
            breakdown.complexity_bonus = 0.03

        # Sentiment bonus: angry/frustrated customers need proper handling
        if self.current_ticket.customer_sentiment == "angry":
            breakdown.complexity_bonus += 0.04
        elif self.current_ticket.customer_sentiment == "frustrated":
            breakdown.complexity_bonus += 0.02

        total_reward = breakdown.base_reward + breakdown.priority_bonus + breakdown.complexity_bonus
        return total_reward, {
            "valid": True,
            "message": f"Classified as {action.category}",
        }

    def _calculate_respond_reward(
        self, action: Action, breakdown: RewardBreakdown
    ) -> Tuple[float, dict]:
        """Calculate reward for respond action with quality assessment."""
        if not self.classified:
            return -0.05, {
                "valid": False,
                "message": "Must classify before responding",
            }

        if not action.content or len(action.content) < 10:
            breakdown.base_reward = 0.05
            return 0.05, {
                "valid": True,
                "message": "Response too short (minimum 10 characters)",
            }

        response_length = len(action.content)

        # Base reward for responding
        breakdown.base_reward = 0.3

        # Quality bonus based on response length - sentiment-aware
        if self.current_ticket.customer_sentiment in ["angry", "frustrated"]:
            # Angry/frustrated customers need longer, more detailed responses
            if response_length >= 200:
                breakdown.quality_bonus = 0.28  # Extra comprehensive for upset customers
            elif response_length >= 120:
                breakdown.quality_bonus = 0.20
            elif response_length >= 50:
                breakdown.quality_bonus = 0.10
            else:
                breakdown.quality_bonus = 0.02
        else:
            # Normal sentiment - standard quality tiers
            if response_length >= 150:
                breakdown.quality_bonus = 0.25
            elif response_length >= 80:
                breakdown.quality_bonus = 0.15
            elif response_length >= 30:
                breakdown.quality_bonus = 0.08
            else:
                breakdown.quality_bonus = 0.02

        # Priority bonus: high-priority issues need better responses
        if self.current_ticket.priority == "high":
            breakdown.priority_bonus = 0.08
        elif self.current_ticket.priority == "medium":
            breakdown.priority_bonus = 0.03

        # SLA urgency bonus
        if self.current_ticket.sla_urgency == "critical":
            breakdown.priority_bonus += 0.05

        # Returning customer loyalty bonus
        if self.current_ticket.is_returning_customer and self.current_ticket.previous_issues_count > 0:
            breakdown.complexity_bonus = 0.05

        # Complexity bonus: complex issues need comprehensive responses
        if self.current_ticket.complexity == "complex":
            breakdown.complexity_bonus += 0.07
        elif self.current_ticket.complexity == "moderate":
            breakdown.complexity_bonus += 0.03

        self.responded = True
        self.response_quality = breakdown.quality_bonus
        agent_message = Message(role="agent", content=action.content)
        self.current_ticket.history.append(agent_message)

        total_reward = (
            breakdown.base_reward
            + breakdown.quality_bonus
            + breakdown.priority_bonus
            + breakdown.complexity_bonus
        )
        return total_reward, {
            "valid": True,
            "message": f"Response recorded ({response_length} chars)",
        }

    def _calculate_escalate_reward(self, breakdown: RewardBreakdown) -> Tuple[float, dict]:
        """Calculate reward for escalate action with priority-aware decision logic."""
        breakdown.base_reward = 0.15

        # Escalation reward depends on ticket priority and needs
        if self.current_ticket.requires_escalation:
            # Correct escalation: reward higher for high-priority issues
            if self.current_ticket.priority == "high":
                breakdown.priority_bonus = 0.20  # Strong reward for correct high-priority escalation
                message = "Correct escalation of high-priority issue"
            else:
                breakdown.priority_bonus = 0.12  # Moderate reward for escalating complex issue
                message = "Appropriate escalation decision"
        else:
            # Unnecessary escalation: strong penalty based on priority
            if self.current_ticket.priority == "low":
                breakdown.priority_bonus = -0.25  # Heavy penalty for escalating low priority
                message = "Unnecessary escalation of low-priority issue"
            else:
                breakdown.priority_bonus = -0.12  # Moderate penalty for unnecessary escalation
                message = "Escalation not required for this issue"

        self.escalated_or_closed = True
        self.done = True

        total_reward = breakdown.base_reward + breakdown.priority_bonus
        return total_reward, {"message": message}

    def _calculate_close_reward(self, breakdown: RewardBreakdown) -> Tuple[float, dict]:
        """Calculate reward for close action with priority-aware decision logic."""
        if not self.responded:
            breakdown.base_reward = -0.1
            message = "Cannot close without responding first"
            return breakdown.base_reward, {
                "valid": False,
                "message": message,
            }

        breakdown.base_reward = 0.15

        # Closure reward depends on ticket priority and complexity
        if not self.current_ticket.requires_escalation:
            # Correct closure for tickets that don't need escalation
            if self.current_ticket.priority == "low":
                breakdown.priority_bonus = 0.18  # Strong reward for closing low-priority correctly
                message = "Appropriate resolution for simple issue"
            else:
                breakdown.priority_bonus = 0.10  # Moderate reward for closing medium-priority
                message = "Appropriate closure decision"
        else:
            # Incorrect closure: agent should have escalated
            if self.current_ticket.priority == "high":
                breakdown.priority_bonus = -0.25  # Heavy penalty for closing high-priority incorrectly
                message = "High-priority issue should have been escalated"
            else:
                breakdown.priority_bonus = -0.15  # Moderate penalty for closing complex issue prematurely
                message = "Complex issue likely requires escalation"

        # Response quality bonus
        if self.response_quality > 0.15:
            breakdown.quality_bonus = 0.08

        self.escalated_or_closed = True
        self.done = True

        total_reward = breakdown.base_reward + breakdown.priority_bonus + breakdown.quality_bonus
        return total_reward, {
            "valid": True,
            "message": message,
        }

    def state(self) -> Dict[str, Any]:
        """Return current environment state. OpenEnv requirement."""
        return {
            "ticket": self.current_ticket.model_dump() if self.current_ticket else None,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "classified": self.classified,
            "responded": self.responded,
            "escalated_or_closed": self.escalated_or_closed,
            "episode_score": self.episode_score,
            "done": self.done,
            "actions_taken": self.actions_taken,
        }
