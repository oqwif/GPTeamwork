import re
from overrides import override
from instance_gpt.instance_gpt import InstanceGPT
from instance_gpt.team_member_instance_gpt import TeamMemberInstanceGPT
from instance_gpt.team_members import TeamMembers

class KanbanBoardGPT(TeamMemberInstanceGPT):
    def __init__(self, name: str, role_description: str, team_members: TeamMembers = None, manager: InstanceGPT = None):
        if team_members is None:
            team_members = TeamMembers()
        self.wiki = f"{name}"
        super().__init__(name, role_description, team_members, manager)

    @override
    def construct_system_prompt(self):
        system_prompt = """
Design a Kanban board system that uses a KanbanBoardGPT instance to manage tasks and the state of the board. The KanbanBoardGPT instance should handle task management, including creating, updating, and moving tasks across the board.

Responses should be broken into two sections: "Response" (communication with the user), and "Wiki" (working memory, including task information, progress, and user request information in markdown format).

Example of improved response format:
Response:
We've created a task for our ProductManagerGPT to define and prioritize key features and moved it to the In Progress column on the Kanban board. We'll provide updates on the progress.

Wiki:

#KanbanBoardGPT Instance

#Kanban Board State:
- To Do:
- In Progress:
  - Define and prioritize key features @ProductManagerGPT
- Done:
"""
        system_prompt += f"Wiki:{self.wiki}\n\n"
        return super().construct_system_prompt() + system_prompt

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
        response = self.extract_response(response_text)
        wiki = self.extract_wiki_entry(response_text)
        self.wiki = wiki

        return await super().process_response(response)
