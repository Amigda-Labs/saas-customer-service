#Load Environments
from dotenv import load_dotenv
load_dotenv()

#Import Agent
from saas_agents.front_desk_agent import front_desk_agent

#Runner
import asyncio 
from agents import run_demo_loop




async def main():
    print("Hello from saas-customer-service!")
    await run_demo_loop(front_desk_agent)


if __name__ == "__main__":
    asyncio.run(main())
