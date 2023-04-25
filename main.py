import openai
import asyncio
from instance_gpt import CoordinatorInstanceGPT, KanbanBoardGPT, PythonDeveloperGPT
from instance_gpt.team_members import TeamMembers
from settings import openai_key

# Set your OpenAI API key
openai.api_key = openai_key

# Ask the user for the decsription of the job
job_description = "Develop a Tic Tac Toe app written in Python and using Kanban methodology" # input("What is the job description? ")
#job_description = "Create an online tshirt store that integrates with shopify. The tshirt store should be able to take orders, process payments, and send emails to customers. The designs should be generated by Dall-e"
#job_description = "Create a company that manufactures and sells electric cars. The company should be able to take orders, process payments, and send emails to customers. The designs should be generated by Dall-e and vetted by a team of engineers."
#job_description = "Build an organisation that hypothesises and tests ideas to combat climate change."
team_members = TeamMembers()
team_members.add_member(KanbanBoardGPT(name="KanbanBoardGPT", role_description="Manages the Kanban board"))
# team_members.add_member(PythonDeveloperGPT(name="DeveloperAliceGPT", role_description="Develops Python code. Is an expert in Python"))
# team_members.add_member(PythonDeveloperGPT(name="DeveloperBobGPT", role_description="Develops Python code. Is an expert in Python"))

headCoordinator = CoordinatorInstanceGPT(
    name = "TeamLeadGPT",
    role_description = "You are the team lead",
    team_members=team_members
)

async def main():
    await headCoordinator.call(user_prompt=job_description, caller_name="Boss")

if __name__ == "__main__":
    asyncio.run(main())