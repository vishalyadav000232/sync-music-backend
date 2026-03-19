import asyncio

async def heartbeat_loop():
    while True:
        print("Heartbeat running...")
       
        await asyncio.sleep(5) 

if __name__ == "__main__":
    asyncio.run(heartbeat_loop())