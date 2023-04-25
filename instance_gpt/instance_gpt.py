import openai
from overrides import final
from settings import openai_model

class InstanceGPT:
    def __init__(self, name: str):
        self.name = name
        self.messages = [{"role": "system", "content" : 'You are a helpful assistant'}]

    # Override this method to provide a system prompt for the instance
    def construct_system_prompt(self):
        return ''

    # Override this method to provide a description of the instance
    def description(self) -> str:
        return f"{self.name}: A helpful assistant instance"

    def title_for_text(self, text: str) -> str:
        messages = [{"role": "system", "content": 'You are a helpful assistant'},
            {"role": "user", "content": f"Create a title for this text:\n{text}"}]
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=messages,
            max_tokens=500,
            temperature=0.0,
            top_p=1,
        )
        completion = response.choices[0]["message"]["content"]
        return completion

    @final
    async def call_openai_chatgpt(self, prompt, caller_name=None):
        """
        Call OpenAI's GPT API to get a response to the prompt

        Args:
            prompt (str): The prompt to send to the API
            caller_name (str, optional): The name of the instance that called this instance. Defaults to None.

        Returns:
            _type_: _description_
        """

        system_prompt = self.construct_system_prompt()
        self.messages[0] = {"role": "system", "content" : system_prompt}
        if caller_name:
            self.messages.append({"role": "user", "content" : f"{caller_name} asked: {prompt}"})
        else:
            self.messages.append({"role": "user", "content" : prompt})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            #model="gpt-4",
            messages=self.messages,
            max_tokens=1000,
            temperature=0.0,
            top_p=1,
        )
        completion = response.choices[0]["message"]["content"]

        bold_caller_name = f"\033[1m@{caller_name}\033[0m"
        bold_name = f"\033[1m@{self.name}\033[0m"
        print(f"{bold_caller_name} -> {bold_name}\n" +
            #   f"\nsystem_prompt:\n\n{system_prompt}\n\n" +
              f"{prompt}\n\n")
        print(f"{bold_name}\n\n")
        print(f"{completion}\n\n")
        print(f"###########################################################################\n\n")

        return completion

    async def call(self, user_prompt, caller_name=None):
        response_text = await self.call_openai_chatgpt(user_prompt, caller_name)
        return await self.process_response(response_text)

    async def process_response(self, response_text: str):
        """
        Process the response from the assistant. Override this method to provide custom processing.
        Ensure to call super.process_response(response_text) to add the response to the messages list

        Args:
            response_text (str) : The response from the assistant

        Returns:
            str: The response text
        """
        self.messages.append({"role": "assistant", "content" : response_text})
        return response_text