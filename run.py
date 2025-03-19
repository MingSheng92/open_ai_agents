import sys
import asyncio  
import time
from src import agents

async def main():
    WORKFLOW_NAME = "Travel assistant workflow"
    GROUP_ID = "travel-agent-conversation"
    USER_ID = "123"

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



    end_time = time.time()
    print("\n" + "=" * 80)
    print(f"✨ Total time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())