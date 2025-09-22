"""
agent.py - ReAct agent implementation using LangChain and Gemini

This file contains:
- ReAct agent class that implements reasoning loops
- Integration with Gemini LLM via LangChain
- Tool calling and structured output handling
- Reasoning trace tracking for debugging
"""

import json
from datetime import datetime
import os
import re
from typing import Dict, Any, Optional, Tuple
from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from tools import (
    get_order,
    get_shipment,
    get_shipment_by_order_id,
    get_order_by_customer_id,
    cancel_order,
)
from prompt import SYSTEM_PROMPT_TEMPLATE

from loguru import logger


class CustomerServiceAgent:

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(api_key=api_key, model_name=model_name)
        self.tools = [
            get_order,
            get_shipment,
            get_shipment_by_order_id,
            get_order_by_customer_id,
            cancel_order,
        ]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.reasoning_trace = []

    def _create_system_prompt(self) -> str:
        """Create system prompt with available tools"""
        tool_descs = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        tool_names = ", ".join([t.name for t in self.tools])
        current_date = datetime.now().strftime("%Y-%m-%d")
        return SYSTEM_PROMPT_TEMPLATE.format(
            tools=tool_descs, tool_names=tool_names, current_date=current_date
        )

    def _extract_action_and_input(
        self, text: str
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        More robust extractor:
        - Finds the Action name (alphanumeric + underscores).
        - Finds 'Action Input:' and extracts the first balanced JSON object following it.
        - Returns (action_name, action_input_dict) or (None, None) if no action found.
        """
        action_match = re.search(r"Action:\s*([A-Za-z0-9_]+)", text)
        if not action_match:
            return None, None
        action_name = action_match.group(1)
        ai_idx = text.find("Action Input:")
        if ai_idx == -1:
            return action_name, {}
        brace_start = text.find("{", ai_idx)
        if brace_start == -1:
            return action_name, {}
        depth = 0
        end_idx = None
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break
        if end_idx is None:
            # Could not find balanced JSON — fall back
            return action_name, {}
        json_text = text[brace_start : end_idx + 1]
        if "'" in json_text and '"' not in json_text:
            return action_name, {}
        try:
            action_input = json.loads(json_text)
        except json.JSONDecodeError:
            return action_name, {}
        return action_name, action_input

    def _execute_action(self, action_name: str, action_input: Dict) -> str:
        """
        Execute the tool
        """
        if action_name not in self.tools_by_name:
            return f"Error: Unknown action '{action_name}'"

        tool = self.tools_by_name[action_name]
        try:
            result = tool.invoke(action_input)
            # Convert dict/list results to JSON for consistent string output
            if isinstance(result, (dict, list)):
                response = result["data"]
                return response
            return str(result)
        except Exception as e:
            return f"Error executing action '{action_name}': {str(e)}"

    def run(self, query: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Run the agent on a given query
        """
        self.reasoning_trace = []

        # Create conversation history with system prompt
        messages = [SystemMessage(content=self._create_system_prompt())]

        # Add current query
        messages.append(HumanMessage(content=query))

        # add chat history to the messages list to provide context to the llm

        for iteration in range(max_iterations):
            try:
                # Get response from LLM
                response = self.llm.invoke(messages)
                logger.info(f"Response: {response}")
                response_text = response.content

                # Add to reasoning trace
                self.reasoning_trace.append(
                    {"iteration": iteration + 1, "response": response_text}
                )

                # check for thought
                # First take everything to the right of "Thought:" from agent response
                # Next check if "Action:" exists in the extracted text. If it does, take what's to the left of it i.e. the actual thought
                # Next check if "Final Answer:" exists extracted text. If it does, take whats to the left of it i.e. the actual thought
                if "Thought:" in response_text:
                    agent_thought = response_text.split("Thought:")[-1].strip()
                    agent_thought = agent_thought.split("Action:")[0].strip()
                    agent_thought = agent_thought.split("Final Answer:")[0].strip()
                    messages.append(AIMessage(content=agent_thought))

                # Check for final answer
                if "Final Answer:" in response_text:
                    final_answer = response_text.split("Final Answer:")[-1].strip()
                    return {
                        "final_answer": final_answer,
                        "reasoning_trace": self.reasoning_trace,
                        "num_iterations": iteration + 1,
                        "success": True,
                    }

                # Extract action and input
                action_name, action_input = self._extract_action_and_input(
                    response_text
                )

                if action_name is None:
                    # No action found, treat as final answer
                    return {
                        "final_answer": response_text,
                        "reasoning_trace": self.reasoning_trace,
                        "num_iterations": iteration + 1,
                        "success": True,
                    }

                # Execute action
                observation = self._execute_action(action_name, action_input)

                # Add observation to conversation
                messages.append(AIMessage(content=response_text))
                messages.append(
                    AIMessage(name=action_name, content=f"Observation: {observation}")
                )

                # Add to reasoning trace
                self.reasoning_trace.append(
                    {
                        "iteration": iteration + 1,
                        "action": action_name,
                        "action_input": action_input,
                        "observation": observation,
                    }
                )

            except Exception as e:
                error_msg = f"Error in iteration {iteration + 1}: {str(e)}"
                self.reasoning_trace.append(
                    {"iteration": iteration + 1, "error": error_msg}
                )
                return {
                    "final_answer": f"I encountered an error: {error_msg}",
                    "reasoning_trace": self.reasoning_trace,
                    "num_iterations": iteration + 1,
                    "success": False,
                }

        # Max iterations reached
        return {
            "final_answer": "I reached the maximum number of iterations without finding a complete answer.",
            "reasoning_trace": self.reasoning_trace,
            "success": False,
        }


def create_agent() -> CustomerServiceAgent:
    """
    Create and return a agent instance
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return CustomerServiceAgent(api_key=api_key)  # add api_key here
