#Load Environments
from dotenv import load_dotenv
load_dotenv()

#Import Agent
from saas_agents.front_desk_agent import front_desk_agent

#Runner
import asyncio 
from agents import run_demo_loop
from agents import Runner



async def main():
    #Using Run Demo Loop
    #await run_demo_loop(front_desk_agent)
    
    #Using Runner
    result = await Runner.run(front_desk_agent, "Hi there what do you do?")
    print(result)



if __name__ == "__main__":
    asyncio.run(main())
