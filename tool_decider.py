# tools/tool_decider.py

import yaml
from pathlib import Path
from openai import AzureOpenAI
import os
from tools.custom_tool import NavigatorTool, CampaignTool 

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_version=os.getenv("AZURE_API_VERSION"),
    api_key=os.getenv("AZURE_API_KEY")
)

class ToolDecider:
    def __init__(self, tasks_yaml_path=None):
        # self.tasks_yaml_path = Path(tasks_yaml_path)
        if tasks_yaml_path is None:
            self.tasks_yaml_path = Path(__file__).parent.parent / "config" / "tasks.yaml"
        else:
            self.tasks_yaml_path = Path(tasks_yaml_path)

    def _load_task_description(self, agent_name: str) -> str:
        if not self.tasks_yaml_path.exists():
            raise FileNotFoundError(f"❌ tasks.yaml not found at: {self.tasks_yaml_path}")

        with open(self.tasks_yaml_path, "r") as f:
            tasks_data = yaml.safe_load(f)

        # Find task that matches the agent
        for task_key, task_info in tasks_data.items():
            if task_info.get("agent") == agent_name:
                return task_info.get("description", "")

        raise ValueError(f"❌ No task found for agent '{agent_name}' in {self.tasks_yaml_path}")

    def decide_tool(self, agent_name: str):
        task_description = self._load_task_description(agent_name)

        prompt = (
            "You are an automation assistant helping an AI agent choose the correct tool.\n"
            "The agent has access to two tools:\n"
            f"Based on this task description:\n\n{task_description}\n\n"
            "Reply ONLY with one of the two tool names: NavigatorTool or CampaignTool."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        tool_name = response.choices[0].message.content.strip()

        if tool_name == "NavigatorTool":
            return NavigatorTool()
        elif tool_name == "CampaignTool":
            return CampaignTool()
        else:
            raise ValueError(f"❌ Invalid tool name from LLM: {tool_name}")