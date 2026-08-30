"""
Coordinator
===========

WHY: Someone needs to be the BOSS.
     The planner plans. The executor executes. The verifier verifies.
     The coordinator TELLS them what to do and WHEN.

WHAT: Orchestrates the entire setup flow:
     1. Create a plan
     2. Execute each step in order
     3. Send progress events to the frontend
     4. Verify everything works
     5. Send the final report

HOW:
     1. Call planner to get steps
     2. For each step:
        a. Emit "step_started" (frontend shows spinner)
        b. Execute the step
        c. Emit "step_done" or "step_failed"
     3. After all steps: run verification
     4. Emit "done" with verification results

THINK OF IT LIKE:
     A construction foreman.
     - Talks to the architect (planner)
     - Tells workers what to do (executor)
     - Checks the work (verifier)
     - Reports progress to the client (frontend)
"""

import uuid
from datetime import datetime, timezone
from app.engine.planner import plan_environment
from app.engine.executor import execute_step
from app.engine.verifier import verify_environment
from app.models.environment import EnvironmentConfig
from app.engine.state import store_environment
from app.events.bus import emit
from app.utils.logger import get_logger

logger = get_logger("coordinator")


async def run_setup(config: EnvironmentConfig) -> str:
    """Run the full setup pipeline.

    This is called when the user clicks "Start Setup."
    It runs the ENTIRE flow from plan to verification.

    Returns: environment_id (UUID)
    """
    logger.info("========== SETUP STARTED ==========")
    start_time = datetime.now(timezone.utc)

    # Generate environment ID
    env_id = str(uuid.uuid4())

    try:
        # PHASE 1: Plan
        logger.info("--- PHASE 1: Planning ---")
        plan = await plan_environment(config)
        total_steps = len(plan.steps)

        # Persist environment record
        store_environment(env_id, plan.network_name)

        await emit("setup_started", {
            "environment_id": env_id,
            "total_steps": total_steps,
            "timestamp": start_time.isoformat(),
        })

        # PHASE 2: Execute
        logger.info("--- PHASE 2: Executing %d steps ---", total_steps)

        for idx, step in enumerate(plan.steps, 1):
            # Tell frontend this step is starting
            await emit("step_started", {
                "step": step.id,
                "step_type": step.type,
                "step_index": idx,
                "total_steps": total_steps,
                "message": f"Starting {step.type}: {step.id}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            # Actually run the step (pass network_name and env_id to executor)
            try:
                result = await execute_step(step, plan.network_name, env_id)
            except Exception as e:
                logger.error("step '%s' raised exception: %s", step.id, str(e))
                await emit("step_failed", {
                    "step": step.id,
                    "error": str(e),
                    "step_index": idx,
                    "total_steps": total_steps,
                    "message": f"Step {step.id} failed: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                return env_id

            # Check result
            if result["code"] != 0:
                logger.error("step '%s' failed (code %d)", step.id, result["code"])
                await emit("step_failed", {
                    "step": step.id,
                    "error": result["stderr"],
                    "step_index": idx,
                    "total_steps": total_steps,
                    "message": f"Step {step.id} failed: {result['stderr'][:200]}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                return env_id

            # Step succeeded
            logger.info("step '%s' completed", step.id)
            await emit("step_done", {
                "step": step.id,
                "step_index": idx,
                "total_steps": total_steps,
                "message": f"Completed: {step.id}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        # PHASE 3: Verify
        logger.info("--- PHASE 3: Verifying ---")
        await emit("verify_started", {
            "message": "Verifying all services...",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        verification = await verify_environment()

        # Check if all services are ready
        all_ready = all(v["status"] == "ready" for v in verification)

        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # PHASE 4: Report
        await emit("done", {
            "environment_id": env_id,
            "verification": verification,
            "success": all_ready,
            "duration_ms": duration_ms,
            "message": "Environment ready!" if all_ready else "Some services failed verification",
            "timestamp": end_time.isoformat(),
        })

        logger.info("========== SETUP COMPLETE (%dms) ==========", duration_ms)

    except Exception as e:
        logger.error("setup failed with unexpected error: %s", str(e))
        await emit("setup_failed", {
            "error": str(e),
            "message": f"Setup failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    return env_id
