
# A class that maintains a list of team members and their roles
from instance_gpt.instance_gpt import InstanceGPT

class TeamMembers:
    def __init__(self):
        self.team_members: dict[str,InstanceGPT] = {}

    def add_member(self, instance: InstanceGPT):
        self.team_members[instance.name] = instance

    def has_member(self, name):
        return name in self.team_members

    def get_member(self, name) -> InstanceGPT:
        if name not in self.team_members:
            return None
        return self.team_members[name]

    def get_members(self):
        return self.team_members

    def call_member(self, name, prompt):
        if name not in self.team_members:
            return None
        return self.team_members[name].call_openai_chatgpt(prompt)

    def call_all_members(self, prompt):
        for name, member in self.team_members.items():
            member.call_openai_chatgpt(prompt)

    def call_all_members_with_response(self, prompt):
        responses = {}
        for name, member in self.team_members.items():
            responses[name] = member.call_openai_chatgpt(prompt)
        return responses

    def call_all_members_with_response_and_create_instance_calls(self, prompt):
        responses = {}
        for name, member in self.team_members.items():
            response = member.call_openai_chatgpt(prompt)
            responses[name] = response
            create_instance_calls = member.extract_create_instance_calls(response)
            member.create_child_coordinators(create_instance_calls)
        return responses

    def call_all_members_with_response_and_create_instance_calls_and_call_instance_calls(self, prompt):
        responses = {}
        for name, member in self.team_members.items():
            response = member.call_openai_chatgpt(prompt)
            responses[name] = response
            create_instance_calls = member.extract_create_instance_calls(response)
            member.create_child_coordinators(create_instance_calls)
            call_instance_calls = member.extract_call_instance_calls(response)
            for instance_name, instance_prompt in call_instance_calls:
                response = member.call_instance(instance_name, instance_prompt)
                responses[instance_name] = response
        return responses

    def call_all_members_with_response_and_create_instance_calls_and_call_instance_calls_and_extract_task_details(self, prompt):
        responses = {}
        for name, member in self.team_members.items():
            response = member.call_openai_chatgpt(prompt)
            responses[name] = response
            create_instance_calls = member.extract_create_instance_calls(response)
            member.create_child_coordinators(create_instance_calls)
            call_instance_calls = member.extract_call_instance

    def team_members_prompt(self):
        prompt = ""
        for team_member in self.team_members.values():
            prompt += team_member.description() + "\n"
        return prompt