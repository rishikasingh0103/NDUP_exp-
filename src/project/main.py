# main.py
import os
from dotenv import load_dotenv
import warnings
from openai import AzureOpenAI
from crew import IRISAutomationCrew
from tools.tool_decider import ToolDecider
# from tools.custom_tool import NavigatorTool, CampaignTool

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
load_dotenv()

# Azure client setup
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_version=os.getenv("AZURE_API_VERSION"),
    api_key=os.getenv("AZURE_API_KEY")
)

# Step 1: Decide agent from user prompt
def decide_agent_from_prompt(user_input):
    prompt = (
        "You're an AI assistant in an automation system with two agents:\n"
        "- 'navigator': handles IRIS Studio creative tasks\n"
        "- 'campaigner': handles marketing/campaign configuration\n"
        "Given the user input, reply with only 'navigator' or 'campaigner'.\n\n"
        f"User: {user_input}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip().lower()
# ToolDecider class to decide which tool to use based on the agent
# Entry point
def run():
    print("🎯 Welcome to IRIS Automation Crew!")
    user_input = input("💬 What do you want me to automate?\n>> ").strip().lower()

    # Step 1: LLM decides agent
    selected_agent = decide_agent_from_prompt(user_input)
    if selected_agent not in ["navigator", "campaigner"]:
        print(f"❌ Could not determine agent from input: '{selected_agent}'")
        return

    # Step 2: LLM decides which tool (based on tasks.yaml)

    try:
        tool = ToolDecider().decide_tool(selected_agent)
        print(f"🤖 LLM selected tool: {tool.__class__.__name__}")
    except Exception as e:
        print(f"❌ Error deciding tool: {e}")
        return

    # Step 3: Get crew from crew.py
    crew_setup = IRISAutomationCrew()

    if selected_agent == "navigator":
        agent = crew_setup.navigator()
        task = crew_setup.creative_task()
    else:
        agent = crew_setup.campaigner()
        task = crew_setup.campaign_task()

    # Step 4: Inject selected tool into agent
    agent.tools = [tool]

    # Step 5: Run the Crew manually
    from crewai import Crew, Process
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    print(f"\n🚀 Running {selected_agent} crew using CrewAI...")
    result = crew.kickoff()
    print(f"\n✅ Done! Output:\n{result}")

if __name__ == "__main__":
    run()
