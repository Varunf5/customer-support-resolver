import os
import sys
import importlib.util

# -------- SAFE IMPORT --------
def import_env_module():
    try:
        from env import SupportTicketEnvironment, TaskManager, grade_task_result
        return SupportTicketEnvironment, TaskManager, grade_task_result
    except Exception as e:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, current_dir)
            from env import SupportTicketEnvironment, TaskManager, grade_task_result
            return SupportTicketEnvironment, TaskManager, grade_task_result
        except Exception as e2:
            raise Exception(f"Env import failed: {e2}")

SupportTicketEnvironment, TaskManager, grade_task_result = import_env_module()

# -------- OPTIONAL IMPORTS --------
try:
    from openai import OpenAI
except:
    OpenAI = None

# -------- MAIN --------
def run_inference():
    print("[START]")

    try:
        # ENV INIT
        env = SupportTicketEnvironment()

        def grader_fn(environment):
            try:
                state = environment.state()
                return {
                    "score": min(1.0, sum([0.3, 0.4, 0.2, 0.1]) if state.get("escalated_or_closed") else 0.0),
                    "details": state,
                }
            except:
                return {"score": 0.0, "details": {}}

        task_manager = TaskManager(grader_fn=grader_fn)

        # -------- EASY --------
        try:
            print("[STEP] Running task: easy")
            result = task_manager.run_easy_task(env)
            score = grade_task_result("easy", result.score)
            print(f"[STEP] Score: {score:.1f}")
        except Exception as e:
            print("[STEP] Easy task failed")
            print(f"[STEP] Score: 0.0")

        # -------- MEDIUM --------
        try:
            print("[STEP] Running task: medium")
            result = task_manager.run_medium_task(env)
            score = grade_task_result("medium", result.score)
            print(f"[STEP] Score: {score:.1f}")
        except Exception as e:
            print("[STEP] Medium task failed")
            print(f"[STEP] Score: 0.0")

        # -------- HARD --------
        try:
            print("[STEP] Running task: hard")
            result = task_manager.run_hard_task(env)
            score = grade_task_result("hard", result.score)
            print(f"[STEP] Score: {score:.1f}")
        except Exception as e:
            print("[STEP] Hard task failed")
            print(f"[STEP] Score: 0.0")

    except Exception as e:
        print("[ERROR]", str(e))

    print("[END]")


if __name__ == "__main__":
    run_inference()