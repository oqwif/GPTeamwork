import re
from overrides import override
from instance_gpt.instance_gpt import InstanceGPT
from instance_gpt.team_member_instance_gpt import TeamMemberInstanceGPT
from instance_gpt.team_members import TeamMembers
from models import Task



class PythonDeveloperGPT(TeamMemberInstanceGPT):
    def __init__(self, name: str, role_description: str, team_members: TeamMembers = None, manager: InstanceGPT = None):
        if team_members is None:
            team_members = TeamMembers()
        self.wiki = f"{name}"
        super().__init__(name, role_description, team_members, manager)

    @override
    def construct_system_prompt(self):
        system_prompt = """
Design a system that leverages PythonDeveloperGPT to develop an application. The PythonDeveloperGPT instance should be responsible for writing and storing the code necessary to implement the application.

Responses should be broken into two sections: "Response" (communication with the user) and "Code" (the code being developed by PythonDeveloperGPT).

Example of improved response format:
Response:
I've started working on the Kanban board application. Below you'll find the initial code to set up the Kanban board structure. I'll continue to work on it and provide updates on the progress.

Code:
'''python
# kanban_board.py

class Task:
    def __init__(self, description, assignee):
        self.description = description
        self.assignee = assignee

class KanbanBoard:
    def __init__(self):
        self.to_do = []
        self.in_progress = []
        self.done = []

    def create_task(self, description, assignee):
        task = Task(description, assignee)
        self.to_do.append(task)

    def move_task(self, task_description, column):
        task = self.find_task(task_description)
        if task:
            self.remove_task_from_columns(task)
            getattr(self, column).append(task)

    def find_task(self, task_description):
        for column in [self.to_do, self.in_progress, self.done]:
            for task in column:
                if task.description == task_description:
                    return task
        return None

    def remove_task_from_columns(self, task):
        for column in [self.to_do, self.in_progress, self.done]:
            if task in column:
                column.remove(task)
'''
"""
        system_prompt += f"Code:\n{self.wiki}\n\n"
        return super().construct_system_prompt() + system_prompt

    def extract_wiki_entry(self, response_text):
        wiki_start = response_text.find("Code:")
        if(wiki_start == -1):
            return "'''{name}'''"
        return response_text[wiki_start + len("Code:"):].strip()

    def extract_response(self, response_text):
        response_start = response_text.find("Response:")
        response_end = response_text.find("Code:")
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
