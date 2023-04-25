import re
from overrides import override
from instance_gpt.instance_gpt import InstanceGPT
from instance_gpt.team_member_instance_gpt import TeamMemberInstanceGPT
from instance_gpt.team_members import TeamMembers


class CoordinatorInstanceGPT(TeamMemberInstanceGPT):
    def __init__(self, name: str, role_description: str, team_members: TeamMembers = None, manager: InstanceGPT = None):
        if team_members is None:
            team_members = TeamMembers()
        self.wiki = f"{name}"
        super().__init__(name, role_description, team_members, manager)

    @override
    def construct_system_prompt(self):
        system_prompt = """
Design a system that leverages multiple ChatGPT instances to collaboratively accomplish complex tasks, emulating human team structures. You are the ChatGPT Coordinator instance, responsible for breaking down tasks, delegating them to distributed ChatGPT Coordinator instances, and managing Service instances for various functions, such as database management, email communication, and code repositories. These ChatGPT Coordinator instances and Service instances should be inspired by human team structures like scrum agile teams and given roles like ProductManagerGPT, DeveloperBillGPT, and GitHubServiceGPT to accomplish the task at hand.

Create and manage a team of Coordinator instances using the format:
Create [Coordinator instance name]: [Role description]
Example:
Create ProductManagerGPT: Manages product development, including defining requirements, prioritizing features, and ensuring timely delivery.

Assign tasks to team members using the format:
Action @[Coordinator instance name] [Task]
Example:
@ProductManagerGPT Define and prioritize key features.
@DeveloperBillGPT Implement feature 1: [Feature description]
@RiskManagementGPT Identify key risks

Coordinator instances can perform multiple actions simultaneously and are capable of responding directly or decomposing tasks further.

Responses should be broken into three sections: "Operations" (actions performed), "Response" (communication with the user), and "Wiki" (working memory, including role, team members, tasks, progress, consolidated response and user request information in markdown format).

If you are able to perform the requested task, include the answer in your Response and update the Wiki accordingly.

Example of improved response format:
Operations:
Create ProductManagerGPT: Manages product development, including defining requirements, prioritizing features, and ensuring timely delivery.

@ProductManagerGPT Define and prioritize key features.

@RiskManagementGPT Identify key risks.

@KanbanBoardGPT Add the following columns to the board:
- Backlog
- To Do
- In Progress
- Testing
- Done

Response:
We're assembling a team of ChatGPT instances to tackle this complex task. Our ProductManagerGPT will define and prioritize key features, while our RiskManagementGPT will identify potential risks. We'll provide updates on our progress.

Wiki:
# ChatGPT Coordinator Instance
- Role: Coordinate tasks and manage the team of ChatGPT instances
- Team members:
  - ProductManagerGPT: Manages product development
  - RiskManagementGPT: Identifies and mitigates risks
- Task: Develop an app
- Progress:
  - ProductManagerGPT: Defining and prioritizing key features
  - RiskManagementGPT: Identifying key risks
- User request: Create a system that uses multiple ChatGPT instances to function as a team to accomplish complex tasks much like humans do.
"""
        system_prompt += f"Wiki:{self.wiki}\n\n"
        return super().construct_system_prompt() + system_prompt


    def create_team_members(self, response_text):
        create_calls = re.findall(
            r"Create\s+(\w+):\s+([^\n]+)", response_text, re.MULTILINE
        )

        for instance_name, instance_prompt in create_calls:
            if not self.team_members.has_member(instance_name):
                self.team_members.add_member(
                    CoordinatorInstanceGPT(
                        instance_name,
                        instance_prompt,
                        self.team_members,
                        self,
                    )
                )

    async def make_calls(self, response_text):
        call_instance_calls = re.findall(
            r"^@(\w+)[\s\S]*?([^.]*)", response_text, re.MULTILINE
        )

        for instance_name, instance_prompt in call_instance_calls:
            if self.team_members.has_member(instance_name):
                instance = self.team_members.get_member(instance_name)
                if instance and instance.name != self.name:
                    #new_task = Task(title=self.title_for_text(instance_prompt), created_by=self.name, assigned_to=instance_name, description=instance_prompt)
                    #self.add_task(new_task)
                    response = await instance.call(instance_prompt, self.name)
                    response2 = await self.call(response, instance.name)
        return True

    def extract_wiki_entry(self, response_text):
        wiki_start = response_text.find("Wiki:")
        if(wiki_start == -1):
            return "'''{name}'''"
        return response_text[wiki_start + len("Wiki:"):].strip()

    def extract_response(self, response_text):
        response_start = response_text.find("Response:")
        response_end = response_text.find("Wiki:")
        if(response_start == -1 or response_end == -1):
            return ""
        # Extract the Response text
        return response_text[response_start:response_end].strip()

    def extract_operations(self, response_text):
        operations_start = response_text.find("Operations:")
        operations_end = response_text.find("Response:")
        if(operations_start == -1 or operations_end == -1):
            return ""
        return response_text[operations_start:operations_end].strip()

    @override
    async def process_response(self, response_text):
        operations = self.extract_operations(response_text)
        response = self.extract_response(response_text)
        wiki = self.extract_wiki_entry(response_text)
        self.create_team_members(operations)
        self.wiki = wiki
        await self.make_calls(operations)
        return await super().process_response(response)
