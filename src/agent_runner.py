from agents import (
    set_default_openai_key,
    Runner,
    RunConfig,
    Agent,
    ModelSettings,
    WebSearchTool,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from openai.types.responses import (
    ResponseCreatedEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseFunctionToolCall,
    ResponseInProgressEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputMessage,
    ResponseTextDeltaEvent,
)
import prompts as prompt
from guardrails import *
from schemas import MessageOutputWithCoT

GPT_MODEL = "gpt-4o-mini-2024-07-18"

# ------------------------------------------------------------------------------------------------
# Specialized Agents
# ------------------------------------------------------------------------------------------------
booking_agent = Agent(  
    name="Booking Specialist",
    model=GPT_MODEL,
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} {prompt.booking_agent}",
    output_type=MessageOutputWithCoT,
)


travel_recommendation_agent = Agent(
    name="Travel Recommendation Specialist",
    model=GPT_MODEL,
    model_settings=ModelSettings(
        tool_choice='auto',
    ),
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} {prompt.travel_reccomendation_agent}",
    tools=[WebSearchTool()],
    output_type=MessageOutputWithCoT,
)   


# ------------------------------------------------------------------------------------------------
# Orchestrator Agent (Tool-based approach)
# ------------------------------------------------------------------------------------------------
reply_agent = Agent(
    name="Reply Agent",
    model=GPT_MODEL,
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} {prompt.reply_agent}",
    output_type=MessageOutput,
    output_guardrails=[non_english_guardrail],
)


query_router_agent = Agent(
    name="Query Router",
    model=GPT_MODEL,
    instructions=(
        f"""{RECOMMENDED_PROMPT_PREFIX} {prompt.query_router_agent}"""
    ),
    tools=[
        booking_agent.as_tool(
            tool_name="consult_booking_specialist",
            tool_description="Use when the user has questions about flight bookings, reservations, or ticketing",
        ),
        travel_recommendation_agent.as_tool(
            tool_name="consult_travel_recommendation_specialist",
            tool_description="Use when the user wants travel destination recommendations or itinerary planning",
        )
    ],
    output_type=MessageOutput,
    handoffs=[reply_agent],
    input_guardrails=[relevance_guardrail, min_length_guardrail, moderation_guardrail],
)



# ------------------------------------------------------------------------------------------------
# Main agent runner 
# ------------------------------------------------------------------------------------------------
class agents:

    def __init__(self, api_key:str, workflow:str, group_id:str, user_id:str):
        set_default_openai_key(api_key)
        self.workflow = workflow
        self.group_id = group_id
        self.user_id = user_id 
        self.result = None 


async def run(self, query):
        """Run the agent with the given query and stream events.

        Args:
            query: The input query to process.

        Returns:
            None: This method streams events and does not return a value.

        Raises:
            AgentInputGuardrailError: If an input guardrail is triggered.
            AgentOutputGuardrailError: If an output guardrail is triggered.
            AgentProcessingError: If an unexpected error occurs during processing.
        """
        # Note: Since this is an async method, we don't wrap it in a try-catch.
        # Instead, we let exceptions propagate to the caller.
        
        result = Runner.run_streamed(
            starting_agent=query_router_agent, 
            input=query,
            run_config=RunConfig(
                workflow_name=self.workflow,
                group_id=self.group_id,
                trace_metadata={
                    "user_id": self.user_id
                },
            ),
        )

        async for event in result.stream_events():
            if event.type == "raw_response_event":
                event_data = event.data
                if isinstance(event_data, ResponseCreatedEvent):
                    agent_name = result.last_agent.name
                    print(f"🏃 Starting `{agent_name}`")
                    print("-" * 50)
                elif isinstance(event_data, ResponseInProgressEvent):
                    print("⏳ Agent response in progress...")
                elif isinstance(event_data, ResponseOutputItemAddedEvent):
                    event_data_item = event_data.item
                    if isinstance(event_data_item, ResponseFunctionToolCall):
                        print(f"🔧 Tool called: {event_data_item.name}")
                        print("\t Arguments: ", end="")
                    elif isinstance(event_data_item, ResponseOutputMessage):
                        print("📝 Drafting response...")
                elif isinstance(event_data, ResponseFunctionCallArgumentsDeltaEvent):
                    event_data_delta = event_data.delta
                    print(event_data_delta, end="", flush=True)
                elif isinstance(event_data, ResponseFunctionCallArgumentsDoneEvent):
                    print("\n✅ Tool call completed!")
                elif isinstance(event_data, ResponseTextDeltaEvent):
                    print(event_data.delta, end="", flush=True)
            elif event.type == "run_item_stream_event":
                if event.name == "tool_output":
                    print("🛠️ Tool output:")
                    print("-" * 40)
                    print(event.item.output)
                    print("-" * 40)
