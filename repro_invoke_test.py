import os, sys, asyncio, traceback
sys.path.insert(0, os.getcwd())
from travel_api.services import invoke_assistant

session={'messages':[{'role':'user','content':'list top 1 resorts in dandeli','name':''}]}

async def run():
    try:
        reply, node = await invoke_assistant(session, 'list top 1 resorts in dandeli')
        print('reply', reply)
        print('node', node)
    except Exception as e:
        print('exception', type(e), e)
        traceback.print_exc()

asyncio.run(run())
