import asyncio
from pathlib import Path
import sys

from mcp import Client, StdioServerParameters


RESOURCE_URI = "taskboard://tasks"
SERVER_PATH = Path(__file__).resolve().with_name("server.py")


async def main() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
        cwd=str(SERVER_PATH.parent),
    )

    async with Client(server) as client:
        result = await client.read_resource(RESOURCE_URI)
        for content in result.contents:
            if hasattr(content, "text"):
                print(content.text)
            elif hasattr(content, "blob"):
                print(content.blob)


if __name__ == "__main__":
    asyncio.run(main())
