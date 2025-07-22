import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from google import genai
from google.genai import types
from dotenv import load_dotenv

import os
import logging

load_dotenv()  # load environment variables from .env
logging.basicConfig(level=logging.CRITICAL) # Set to DEBUG for more verbose output or CRITICAL for less
logger = logging.getLogger(__name__)

SCHEMA_SUMMARY = """
You have access to a PostgreSQL database with the following table:

Table: anomaly_data
- process_id: INTEGER — the unique identifier of a process
- anomaly_detected: BOOLEAN — true if the process detected an anomaly, false otherwise
- time: TIMESTAMPTZ — when the status was recorded

Common queries include:
- Percentage of anomalies detected for a process over a time window
- Whether any anomalies were detected during a period
- Average or latest anomaly status per process
"""

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.google = genai.Client(api_key=os.getenv("GOOGLE_API_KEY")) 
        # methods will go here

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools

    async def process_query(self, query: str) -> str:
        """Process a query using Gemini and available tools"""
        contents = [
            types.Content(
                role="user", parts=[types.Part(text=SCHEMA_SUMMARY)]
            ),
            types.Content(
                role="user", parts=[types.Part(text=query)]
            )
        ]

        mcp_tools = await self.session.list_tools()

        # Initial Gemini API call
        # response = self.google.messages.create(
        #     model="claude-3-5-sonnet-20241022",
        #     max_tokens=1000,
        #     messages=messages,
        #     tools=available_tools
        # )
        tools = [
            types.Tool(
                function_declarations=[
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            k: v
                            for k, v in tool.inputSchema.items()
                            if k not in ["additionalProperties", "$schema"]
                            },
                        }
                    ]
                )
                for tool in mcp_tools.tools
            ]
        
        response = self.google.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0,
                tools=tools,
            ),
        )

        logging.debug("`Handled first response from Geminis")

        # Process response and handle tool calls
        # EXAMPLE: Has there been any downtime in the past 24 hours for process_id 1111 based on the status column?
        final_text = []

        assistant_message = []
        logging.debug("At top of loop")
        if response.candidates[0].content.parts[0].function_call:
            logging.debug("Tool call detected")

            tool_call = response.candidates[0].content.parts[0].function_call
            tool_name = tool_call.name
            tool_args = tool_call.args
            logging.debug(f"Tool call: {tool_name} with args {tool_args}")

    
            # Execute tool call
            result = await self.session.call_tool(tool_name, tool_args)
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")


            # Create a function response part
            function_response_part = types.Part.from_function_response(
                name=tool_name,
                response={"result": result},
            )

            # Append function call and result of the function execution to contents
            contents.append(response.candidates[0].content) # Append the content from the model's response.
            contents.append(types.Content(role="user", parts=[function_response_part])) # Append the function response
             
            final_response = self.google.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    temperature=0,
                    tools=tools,
                ),
                contents=contents,
            )
            logging.debug("Final response from Gemini received")
            final_text.append(final_response.candidates[0].content.parts[0].text)
        else:
            logging.debug("No tool call detected, processing response directly")
            final_text.append(response.text)
            contents.append(response.text)


        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())
