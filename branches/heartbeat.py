async def branch_logic(self):
    """Heartbeat branch — steady pulse every interval."""
    while self.active:
        print(f"[HEARTBEAT] {self.name} alive at {time.time()}")
        import asyncio
        await asyncio.sleep(self.config.get("interval", 2))
