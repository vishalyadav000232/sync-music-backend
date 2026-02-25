import asyncio

async def heartbeat_loop():
    while True:
        print("Heartbeat running...")
        # call your sync functions here
        await asyncio.sleep(5)  # runs every 5 seconds

if __name__ == "__main__":
    asyncio.run(heartbeat_loop())