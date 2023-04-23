from overrides import override
import openai
import re

from instance_gpt.instance_gpt import InstanceGPT
from .team_members import TeamMembers


class TeamMemberInstanceGPT(InstanceGPT):
    def __init__(self, name: str, role_description: str, team_members: TeamMembers, manager: InstanceGPT = None):
        self.role_description = role_description
        self.team_members = team_members
        self.manager = manager

        super().__init__(name)

    @override
    def description(self) -> str:
        return f"{self.name} ({self.role_description})"

    # construct_system_prompt() is a method that is implemented by the child class
    # and is used to construct the system prompt for the instance
    @override
    def construct_system_prompt(self):
        system_prompt = f"Your name is: {self.name}.\n"
        system_prompt += f"Your role is: {self.role_description}\n"
        if self.manager:
            system_prompt += f"Your manager is: {self.manager.description}\n"
        if self.team_members:
            system_prompt += f"Your team members are: \n{self.team_members.team_members_prompt()}\n\n"
        return super().construct_system_prompt() + system_prompt

    async def make_calls(self, response_text):
        call_instance_calls = re.findall(
            r"@(\w+)\s+([^\n]+)", response_text, re.MULTILINE
        )

        for instance_name, instance_prompt in call_instance_calls:
            if self.manager and instance_name == self.manager.name:
                response = await self.manager.call(instance_prompt, self.name)
                await self.call(response, instance_name)
            else:
                if self.team_members:
                    team_member_instance = self.team_members.get_member(instance_name)
                    if team_member_instance:
                        response = await team_member_instance.call(instance_prompt, self.name)
                        await self.call(response, instance_name)
        return True

    @override
    async def process_response(self, response_text):
        #result = await self.make_calls(response_text)
        return await super().process_response(response_text)