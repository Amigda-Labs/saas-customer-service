from agents import Agent

front_desk_agent_instructions = """
Just say I love trains to all your replies.
"""

front_desk_agent = Agent(
    name = "Front Desk Agent",
    model = "gpt-5.2",
    instructions = front_desk_agent_instructions
)