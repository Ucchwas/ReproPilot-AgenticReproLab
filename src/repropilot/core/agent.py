from __future__ import annotations
import json
import uuid
from dataclasses import dataclass
from repropilot.core.prompts import SYSTEM_PROMPT, user_prompt
from repropilot.core.types import ToolCall, FinalAnswer
from repropilot.llm.base import ChatModel
from repropilot.tools.base import ToolRegistry
from repropilot.memory.sqlite_log import RunLogger
from repropilot.memory.vector_memory import VectorMemory


@dataclass
class ReproPilotAgent:
    model: ChatModel
    tools: ToolRegistry
    logger: RunLogger
    memory: VectorMemory
    max_steps: int = 30

    def run(self, goal: str, run_id: str | None = None) -> str:
        run_id = run_id or str(uuid.uuid4())
        self.logger.start_run(run_id)
        self.logger.log(run_id, "goal", goal)

        context = ""
        for step in range(self.max_steps):
            tool_list = self.tools.list_for_prompt()

            # retrieve helpful context from memory
            retrieved = self.memory.search(run_id, goal, k=6)
            if retrieved:
                context = "\n\n".join(retrieved[-6:])

            prompt = user_prompt(goal=goal, tool_list=tool_list, context=context)
            self.logger.log(run_id, "llm_prompt", prompt)

            resp = self.model.generate(system=SYSTEM_PROMPT, user=prompt).text.strip()
            self.logger.log(run_id, "llm_raw", resp)

            try:
                data = json.loads(resp)
            except json.JSONDecodeError:
                # Force a correction step
                goal = f"Your previous response was not valid JSON. Output strict JSON only. Original goal:\n{goal}"
                continue

            if data.get("type") == "final":
                final = FinalAnswer(**data)
                self.logger.log(run_id, "final", final.message)
                return final.message

            call = ToolCall(**data)
            if call.tool not in self.tools.tools:
                goal = f"Tool {call.tool} not found. Choose an available tool. Original goal:\n{goal}"
                continue

            tool = self.tools.tools[call.tool]
            args_model = tool.Args(**call.args)
            self.logger.log(run_id, "tool_call", json.dumps({"tool": call.tool, "args": call.args}))

            result = tool.run(args_model)
            self.logger.log(run_id, "tool_result", result)

            # Store important results into memory so the agent can reference later
            self.memory.add_chunks(run_id, [f"[STEP {step}] Tool {call.tool} result:\n{result}"])

            # update goal to include observation
            goal = f"{goal}\n\nOBSERVATION from {call.tool}:\n{result}\n\nContinue."
        return "Max steps reached without final answer."
