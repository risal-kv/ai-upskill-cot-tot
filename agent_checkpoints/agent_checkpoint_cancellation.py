"""
Cancellation-focused ReAct agent using Chain-of-Thought formatting.
"""

import os
import json
from typing import Dict, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from tools import (
    get_order,
    get_shipment,
    get_shipment_by_order_id,
    get_order_by_customer_id,
    cancel_order,
)
from prompt import CANCELLATION_PROMPT_TEMPLATE
from loguru import logger


class CancellationSupportAgent:
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(api_key=api_key, model_name=model_name)
        self.tools = [
            get_order,
            get_shipment,
            get_shipment_by_order_id,
            get_order_by_customer_id,
            cancel_order,
        ]
        self.agent = create_react_agent(
            self.llm, self.tools, prompt=self._create_prompt()
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            return_intermediate_steps=True,
        )
        self.reasoning_trace = []

    def _create_prompt(self):
        template = CANCELLATION_PROMPT_TEMPLATE
        return ChatPromptTemplate.from_template(template)

    def run(self, query: str) -> Dict[str, Any]:
        self.reasoning_trace = []
        try:
            response = self.agent_executor.invoke({"input": query})
            logger.info(f"Response: {response}")
            self._format_steps(response)
            return {
                "final_answer": response.get("output", ""),
                "reasoning_trace": self.reasoning_trace,
                "num_iterations": len(self.reasoning_trace),
                "success": True,
            }
        except Exception as e:
            logger.exception("Cancellation agent error")
            return {
                "final_answer": f"I encountered an error: {str(e)}",
                "reasoning_trace": self.reasoning_trace,
                "num_iterations": 0,
                "success": False,
            }

    def _format_steps(self, response: Dict[str, Any]) -> None:
        for item in response.get("intermediate_steps", []):
            if isinstance(item, tuple) and len(item) == 2:
                action, observation = item
            else:
                self.reasoning_trace.append(
                    {
                        "iteration": len(self.reasoning_trace) + 1,
                        "response": f"Observation: {json.dumps(item, default=str)}",
                    }
                )
                continue

            thought = getattr(action, "log", None) or getattr(action, "thought", None)
            if thought:
                self.reasoning_trace.append(
                    {
                        "iteration": len(self.reasoning_trace) + 1,
                        "response": f"Thought: {thought}",
                    }
                )

            action_name = getattr(action, "tool", None) or getattr(
                action, "action", None
            )
            action_input = getattr(action, "tool_input", None) or getattr(
                action, "action_input", None
            )

            self.reasoning_trace.append(
                {
                    "iteration": len(self.reasoning_trace) + 1,
                    "response": f"Action: {action_name}",
                    "action_input": action_input,
                }
            )

            if isinstance(observation, (dict, list)):
                obs_text = json.dumps(observation, indent=2)
            else:
                obs_text = str(observation)

            self.reasoning_trace.append(
                {
                    "iteration": len(self.reasoning_trace) + 1,
                    "response": f"Observation: {obs_text}",
                }
            )


def create_agent() -> CancellationSupportAgent:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return CancellationSupportAgent(api_key=api_key)
