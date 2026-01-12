"""
Starts the application

Usage:
    uv run -m core.main
"""
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

#Context
from core.context import SharedContext
from datetime import datetime

#Session
from agents import SQLiteSession

#Guardrails
from agents.exceptions import InputGuardrailTripwireTriggered

#Trace
from agents import trace

async def main():
    #Create initial context
    context = SharedContext(
        name = "",
        contact_num="",
        start_time=datetime.now(),
        end_time=datetime.now()
    )


    #Using Run Demo Loop
    #await run_demo_loop(front_desk_agent, context=context)

    # Using Runner - More controlled
    # Use a unique ID per user/conversation in production
    session = SQLiteSession("front_desk_session")
    
    
    config = RunConfig(
        trace_include_sensitive_data=True,  #Content invisibility
        #tracing_disabled=True, #Completely zero visibility
        workflow_name = "Front Desk Agent Workflow"
    )

    with trace(
        workflow_name="Front Desk Session",
        group_id=session.session_id,  # Optional: link traces by session
        metadata={"session_type": "front_desk"}  # Optional metadata
    ):
        while True:
            user_input = input("Ask anything: ").strip()

            if user_input.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break

            try:
                result = await Runner.run(
                    front_desk_agent,
                    user_input,
                    context=context,
                    session=session,
                    run_config=config
                )
                print(result)
            except InputGuardrailTripwireTriggered as e:
                # Catch for Guardrail blocking the input
                # The blocked message is NOT added to session history
                output_info = e.guardrail_result.output.output_info
                print(f"\n🚫 Request blocked by security guardrail!")
                print(f"   Reason: {output_info.reasoning}")
                print(f"   Threat level: {output_info.threat_level}")
                if output_info.abuse_type:
                    print(f"   Type: {output_info.abuse_type}")
                print("\nPlease make a reasonable booking request.\n")
                # Loop continues - conversation history remains clean



if __name__ == "__main__":
    asyncio.run(main())
