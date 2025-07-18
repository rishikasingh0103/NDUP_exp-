from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class IRISAutomationCrew():
    """IRIS Automation crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def navigator(self) -> Agent:
        return Agent(
            config=self.agents_config['navigator'],
            tools=[],  # No tool assigned here
            verbose=True
        )

    @agent
    def campaigner(self) -> Agent:
        return Agent(
            config=self.agents_config['campaigner'],
            tools=[],  # No tool assigned here
            verbose=True
        )

    @task
    def creative_task(self) -> Task:
        return Task(
            config=self.tasks_config['creative_task'],
        )

    @task
    def campaign_task(self) -> Task:
        return Task(
            config=self.tasks_config['campaign_task'],
        )

    @crew
    def navigator_crew(self) -> Crew:
        return Crew(
            agents=[self.navigator()],
            tasks=[self.creative_task()],
            process=Process.sequential,
            verbose=True
        )

    @crew
    def campaigner_crew(self) -> Crew:
        return Crew(
            agents=[self.campaigner()],
            tasks=[self.campaign_task()],
            process=Process.sequential,
            verbose=True
        )