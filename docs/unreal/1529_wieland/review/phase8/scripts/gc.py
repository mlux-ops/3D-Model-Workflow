import unreal, asyncio
unreal.SystemLibrary.collect_garbage()
await asyncio.sleep(20.0)
"collected"
