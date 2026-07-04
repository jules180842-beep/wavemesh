async def branch_logic(self):
    """Monitor branch — checks system health and logs it."""
    while self.active:
        print(f"[MONITOR] Checking system health...")
        print(f"[MONITOR] Active branches: {len(STATE['branches'])}")
        import asyncio
        await asyncio.sleep(self.config.get("interval", 5))
