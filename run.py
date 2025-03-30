import os
import sys
import asyncio  
import time
import logging 
from src import agents, AgentInputGuardrailError, AgentOutputGuardrailError, AgentProcessingError
from agents import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered
)
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 
async def main():
    WORKFLOW_NAME = "Travel assistant workflow"
    GROUP_ID = "travel-agent-conversation"
    USER_ID = "123"
    API_KEY = os.enciron.get("OPEN_API_KEY", "")

    load_dotenv()

    # ------------------------------------------------------------------------------------------------
    # Initialize OpenAI client
    # ------------------------------------------------------------------------------------------------
    
    # client = AsyncOpenAI()

    # retrieve user query from command line arguments  
    if len(sys.argv) < 2: 
        # when user didnt include query 
        print("Usage: python run.py 'Your question here.'")
        
        return 
    
    query = sys.argv[1]    
    print("🔍 Processing your query: ", query)
    start_time = time.time()
    print("=" * 80)

    try:
        # initialize and start the agent loop
        travel_assistant = agents(API_KEY, WORKFLOW_NAME, GROUP_ID, USER_ID)
        await travel_assistant.run(query)
    except InputGuardrailTripwireTriggered as e:
        # Wrap the guardrail exception in our custom exception
        guardrail_output = e.guardrail_result.output.output_info
        raise AgentInputGuardrailError(
            message=f"Input guardrail triggered: {guardrail_output.error_message}",
            guardrail_output=guardrail_output
        ) from e
    except OutputGuardrailTripwireTriggered as e:
        # Wrap the guardrail exception in our custom exception
        guardrail_output = e.guardrail_result.output.output_info
        raise AgentOutputGuardrailError(
            message=f"Output guardrail triggered: {guardrail_output.error_message}",
            guardrail_output=guardrail_output
        ) from e
    except Exception as e:
        # Wrap any other unexpected exception
        raise AgentProcessingError(f"Unexpected error during agent processing: {e}") from e

    end_time = time.time()
    print("\n" + "=" * 80)
    print(f"✨ Total time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    try:
        # Run the async main function
        asyncio.run(main())
    except AgentInputGuardrailError as e:
        logger.error(f"Input guardrail error: {e}")
        logger.info(f"Guardrail output: {e.guardrail_output}")
        # Handle the error (e.g., exit with a specific status code)
        exit(1)
    except AgentOutputGuardrailError as e:
        logger.error(f"Output guardrail error: {e}")
        logger.info(f"Guardrail output: {e.guardrail_output}")
        # Handle the error differently if needed
        exit(1)
    except AgentProcessingError as e:
        logger.error(f"Processing error: {e}")
        # Handle unexpected errors
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)