#Load Environments
from dotenv import load_dotenv
from pydantic import config
load_dotenv()

#Import Agent
from saas_agents.front_desk_agent import front_desk_agent

#Runner
import asyncio 
from agents import run_demo_loop
from agents import Runner, RunConfig



async def main():
    #Using Run Demo Loop
    await run_demo_loop(front_desk_agent)
    
    #Using Runner - More controlled
    #config = RunConfig(
    #    trace_include_sensitive_data=False,  #Content invisibility
    #    #tracing_disabled=True, #Completely zero visibility
    #    workflow_name = "Front Desk Agent Workflow"
    #)

    #result = await Runner.run(front_desk_agent, "Hi there what do you do?", run_config=config)
    #print(result)



if __name__ == "__main__":
    asyncio.run(main())
