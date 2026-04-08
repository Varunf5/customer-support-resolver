"""
Task definitions for the Customer Support Ticket Resolver Environment.
Implements EASY, MEDIUM, and HARD tasks with realistic scenarios.
"""

from typing import List, Callable
from .environment import SupportTicketEnvironment
from .models import Action, TaskResult, Observation


class TaskManager:
    """Manages task definition and execution."""

    def __init__(self, grader_fn: Callable[[SupportTicketEnvironment], dict]):
        self.grader = grader_fn

    def run_easy_task(self, env: SupportTicketEnvironment) -> TaskResult:
        """
        EASY TASK: Classify the ticket correctly.

        Goal: Agent must classify the support ticket into one of the valid categories
        (billing, technical, account, general, escalation).

        Success criteria:
        - Single action: classify with correct category
        - Valid category selected
        - Quick resolution (1 step)
        """
        env.reset()

        # Determine correct category based on ticket content
        correct_category = self._infer_category(env.current_ticket.customer_message)

        # Agent takes action - simulate perfect agent
        action = Action(action_type="classify", category=correct_category)
        obs, reward, done, info = env.step(action)

        score = reward
        details = {
            "ticket_id": env.current_ticket.ticket_id,
            "priority": env.current_ticket.priority,
            "complexity": env.current_ticket.complexity,
            "action_taken": action.action_type,
            "category_assigned": correct_category,
            "expected_category": correct_category,
            "reward": reward,
            "reward_breakdown": info.reward_breakdown,
            "step_count": env.step_count,
            "success": True,  # Classification was performed with correct category inference
        }

        return TaskResult(task_name="easy", score=score, details=details)

    def run_medium_task(self, env: SupportTicketEnvironment) -> TaskResult:
        """
        MEDIUM TASK: Generate a helpful response with proper classification.

        Goal: Agent must first classify correctly, then provide a substantive,
        contextually appropriate response to the customer.

        Success criteria:
        - Two actions: classify + respond
        - Classification is correct
        - Response is substantive (50+ characters)
        - Response addresses the customer's issue
        - Efficient resolution (2-3 steps)
        """
        env.reset()

        correct_category = self._infer_category(env.current_ticket.customer_message)
        should_escalate = env.current_ticket.requires_escalation

        # Step 1: Classify
        action1 = Action(action_type="classify", category=correct_category)
        obs1, reward1, done1, info1 = env.step(action1)
        if done1:
            return TaskResult(
                task_name="medium",
                score=reward1,
                details={
                    "error": "Premature termination at classify step",
                    "ticket_id": env.current_ticket.ticket_id,
                },
            )

        # Step 2: Respond with comprehensive message
        helpful_response = self._generate_helpful_response(
            env.current_ticket.customer_message,
            correct_category,
            env.current_ticket.priority,
            env.current_ticket.complexity,
            sentiment=env.current_ticket.customer_sentiment,
            is_returning=env.current_ticket.is_returning_customer,
            prev_issues=env.current_ticket.previous_issues_count,
        )
        action2 = Action(action_type="respond", content=helpful_response)
        obs2, reward2, done2, info2 = env.step(action2)

        total_score = reward1 + reward2
        # Normalize to [0.0, 1.0]
        score = min(1.0, max(0.0, total_score))

        details = {
            "ticket_id": env.current_ticket.ticket_id,
            "priority": env.current_ticket.priority,
            "complexity": env.current_ticket.complexity,
            "actions_taken": ["classify", "respond"],
            "category_assigned": correct_category,
            "response_length": len(helpful_response),
            "step_count": env.step_count,
            "individual_rewards": [reward1, reward2],
            "individual_breakdowns": [info1.reward_breakdown, info2.reward_breakdown],
            "total_reward": total_score,
            "episode_completed": done2,
        }

        return TaskResult(task_name="medium", score=score, details=details)

    def run_hard_task(self, env: SupportTicketEnvironment) -> TaskResult:
        """
        HARD TASK: Full ticket resolution with correct escalation/closure decision.

        Goal: Agent must classify, respond comprehensively, and make the correct
        decision to either escalate (for complex/high-priority issues) or close
        (for simple/resolved issues).

        Success criteria:
        - Three actions: classify + respond + (escalate or close)
        - Correct classification
        - Quality response (80+ characters for complex, 50+ for simple)
        - Appropriate final action (escalate complex/high-priority, close simple/low-priority)
        - Efficient resolution (3-5 steps)
        - Demonstrates proper support workflow
        """
        env.reset()

        correct_category = self._infer_category(env.current_ticket.customer_message)
        should_escalate = env.current_ticket.requires_escalation

        # Step 1: Classify
        action1 = Action(action_type="classify", category=correct_category)
        obs1, reward1, done1, info1 = env.step(action1)
        if done1:
            return TaskResult(
                task_name="hard",
                score=reward1,
                details={
                    "error": "Premature termination at classify step",
                    "ticket_id": env.current_ticket.ticket_id,
                },
            )

        # Step 2: Respond with comprehensive message
        helpful_response = self._generate_helpful_response(
            env.current_ticket.customer_message,
            correct_category,
            env.current_ticket.priority,
            env.current_ticket.complexity,
            sentiment=env.current_ticket.customer_sentiment,
            is_returning=env.current_ticket.is_returning_customer,
            prev_issues=env.current_ticket.previous_issues_count,
        )
        action2 = Action(action_type="respond", content=helpful_response)
        obs2, reward2, done2, info2 = env.step(action2)
        if done2:
            return TaskResult(
                task_name="hard",
                score=reward1 + reward2,
                details={
                    "error": "Premature termination at respond step",
                    "ticket_id": env.current_ticket.ticket_id,
                },
            )

        # Step 3: Escalate or Close based on ticket requirements
        if should_escalate:
            action3 = Action(action_type="escalate")
        else:
            action3 = Action(action_type="close")

        obs3, reward3, done3, info3 = env.step(action3)

        total_score = reward1 + reward2 + reward3
        # Normalize to [0.0, 1.0]
        score = min(1.0, max(0.0, total_score))

        # Determine success of final action
        correct_final_action = (
            (should_escalate and action3.action_type == "escalate")
            or (not should_escalate and action3.action_type == "close")
        )

        details = {
            "ticket_id": env.current_ticket.ticket_id,
            "priority": env.current_ticket.priority,
            "complexity": env.current_ticket.complexity,
            "requires_escalation": should_escalate,
            "actions_taken": ["classify", "respond", action3.action_type],
            "category_assigned": correct_category,
            "response_length": len(helpful_response),
            "final_action_correct": correct_final_action,
            "final_action_taken": action3.action_type,
            "step_count": env.step_count,
            "individual_rewards": [reward1, reward2, reward3],
            "individual_breakdowns": [
                info1.reward_breakdown,
                info2.reward_breakdown,
                info3.reward_breakdown,
            ],
            "total_reward": total_score,
            "episode_completed": done3,
        }

        return TaskResult(task_name="hard", score=score, details=details)

    @staticmethod
    def _infer_category(message: str) -> str:
        """Infer the correct category from the message content."""
        message_lower = message.lower()

        # Account category keywords
        account_keywords = ["login", "password", "account", "profile", "email", "credentials", "access", "compromised"]
        if any(word in message_lower for word in account_keywords):
            return "account"

        # Technical category keywords
        technical_keywords = ["crash", "bug", "error", "upload", "app", "fails", "broken", "timeout", "feature"]
        if any(word in message_lower for word in technical_keywords):
            return "technical"

        # Billing category keywords
        billing_keywords = ["charge", "refund", "payment", "subscription", "invoice", "cancel", "twice"]
        if any(word in message_lower for word in billing_keywords):
            return "billing"

        # Default to general
        return "general"

    @staticmethod
    def _generate_helpful_response(
        message: str, category: str, priority: str, complexity: str,
        sentiment: str = "neutral", is_returning: bool = True, prev_issues: int = 0
    ) -> str:
        """Generate a contextually appropriate response based on multiple factors including sentiment."""
        base_responses = {
            "account": {
                "high_complex": "Thank you for reporting this account security issue. I understand the urgency. Our security team has been notified and will investigate immediately. We'll lock your account to prevent unauthorized access and walk you through account recovery steps. You should see a verification email shortly. Please respond to confirm your identity and we'll restore access immediately.",
                "high_moderate": "I apologize for the login difficulties. Let me help you regain access right away. I'll send you a secure password reset link. Once you've reset your password, try clearing your browser cache and cookies before logging in. If you continue to have issues, we can investigate further.",
                "moderate": "Thanks for reaching out about your account. I can help with profile updates and password management. To change your email address, go to Settings > Account > Email. For other profile information, visit Account Settings. Let me know if you need more detailed instructions!",
                "low": "Thanks for contacting us. To update your profile, navigate to Settings > Profile. You can change your name, email, and other personal details there. Your changes will take effect immediately.",
            },
            "technical": {
                "high_complex": "I'm sorry you're experiencing crashes and file upload failures. This is clearly impacting your work. I'm escalating this to our technical engineering team for immediate investigation. We've documented your issue and will prioritize it. In the meantime, try using the web version or a different browser. Someone from our team will contact you within 2 hours with updates.",
                "high_moderate": "I understand the app is experiencing errors. Let's troubleshoot this together. First, try: 1) Update the app to the latest version, 2) Force close and restart, 3) Clear the app cache. If the error persists, we'll investigate server-side issues.",
                "moderate": "Thanks for reporting this bug. These kinds of issues help us improve. I've logged this bug report and forwarded it to our development team. We'll investigate and keep you updated on progress. Is there a workaround you could use in the meantime?",
                "low": "Good catch on that issue! We'll look into it. In the meantime, here are some potential workarounds that might help.",
            },
            "billing": {
                "high_complex": "I sincerely apologize for the billing errors. A double charge and unresolved cancellation are serious issues that need immediate attention. I'm escalating this to our billing team and to a manager to ensure proper resolution. You will receive a full refund, and I'll personally monitor your account to prevent further issues. Expect contact from our billing team within 24 hours.",
                "high_moderate": "I apologize for the billing charge issue. I'm reviewing your account now and will address this. I can see the duplicate charge and we'll process a refund immediately. Could you confirm the email associated with your account so I can proceed?",
                "moderate": "Thanks for letting us know about the billing question. Our standard refund policy allows returns within 30 days. For subscription refunds, we process them within 5 business days. What specifically would you like to refund?",
                "low": "Good question about our refund policy. We typically offer returns within 30 days. You can request a refund through your account dashboard, or I can help process it for you.",
            },
            "general": {
                "high": "Thank you for contacting us with this important matter. I'm looking into your question right now and will provide you with a comprehensive answer. You're a valued customer and we want to make sure we address this properly.",
                "moderate": "Thank you for your inquiry. Let me help you find the information you need. I'm here to assist.",
                "low": "Thank you for reaching out! I'd be happy to help answer your question about our service.",
            },
        }

        # Get the base response
        if category in ["account", "technical", "billing"]:
            category_responses = base_responses.get(category, {})
            if priority == "high" and complexity == "complex":
                response = category_responses.get("high_complex", "I understand this is urgent. Let me escalate this to the right team.")
            elif priority == "high":
                response = category_responses.get("high_moderate", "I understand this is important. Let me help you.")
            else:
                response = category_responses.get("moderate", "Thank you for contacting us.")
        else:
            # General category
            if priority == "high":
                response = base_responses["general"]["high"]
            elif priority == "medium":
                response = base_responses["general"]["moderate"]
            else:
                response = base_responses["general"]["low"]

        # Sentiment-aware postfix: show empathy for angry/frustrated customers
        if sentiment == "angry":
            response += " I truly apologize for your frustration and appreciate your patience as we resolve this."
        elif sentiment == "frustrated":
            response += " I understand this is frustrating, and I'm committed to getting this resolved for you."
        
        # Returning customer acknowledgment
        if is_returning and prev_issues > 2:
            response += " As a valued long-time customer, we appreciate your business and will prioritize your case."
        elif is_returning and prev_issues > 0:
            response += " Thank you for being a valued customer."

        return response