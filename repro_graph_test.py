import os, sys
sys.path.insert(0, os.getcwd())
from langchain_core.messages import HumanMessage
from travel_agents.graph import graph

messages = [HumanMessage(content='list top 1 resorts in dandeli')]
print('starting graph astream...')

import asyncio

async def run_graph():
    try:
        async for event in graph.astream({'messages': messages}):
            print('event', type(event), event)
    except Exception as e:
        import traceback
        print('graph exception', type(e), e)
        traceback.print_exc()

asyncio.run(run_graph())
