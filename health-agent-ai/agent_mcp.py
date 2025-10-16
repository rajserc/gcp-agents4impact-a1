import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, \
                    StdioServerParameters, StdioConnectionParams

# IMPORTANT: Replace this with the ABSOLUTE path to your adk_server.py script
PATH_TO_YOUR_MCP_SERVER_SCRIPT = "/path/to/your/adk_server.py"

if PATH_TO_YOUR_MCP_SERVER_SCRIPT == "None":
    print("WARNING: PATH_TO_YOUR_MCP_SERVER_SCRIPT is not set. Please update it in agent.py.")
    # Optionally, raise an error if the path is critical

root_agent = LlmAgent(
    model=os.getenv("MODEL"),
    name='web_reader_mcp_client_agent',
    instruction="Use the 'load_web_page' tool to fetch content from a URL provided by the user.",
    ## Add the MCPToolset below:
    tools=[
    MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=[
                "-y",
                "@modelcontextprotocol/server-google-maps",
            ],
            env={
                "GOOGLE_MAPS_API_KEY": google_maps_api_key
            }
        ),
        timeout=15,
        ),
    )
],
)



    # "mcpServers": {
    #    "datacommons-mcp": {
    #        "command": "uvx",
    #         "args": [
    #             "datacommons-mcp@latest",
    #             "serve",
    #             "stdio"
    #         ],
    #         "env": {
    #             "DC_API_KEY": "<your Data Commons API key>"
    #         },
    #         "trust": true
    #     }
    # }

# tools=[
#     MCPToolset(
#     connection_params=StdioConnectionParams(
#         server_params=StdioServerParameters(
#             command="python3", # Command to run your MCP server script
#             args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT], # Argument is the path to the script
#         ),
#         timeout=15,
#         ),
#         tool_filter=['load_web_page'] # Optional: ensure only specific tools are loaded
#     )
# ],

# ### cd ~/adk_mcp_tools
# cat << EOF > google_maps_mcp_agent/.env
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-00-c43f770ddbd4
# GOOGLE_CLOUD_LOCATION=us-east1
# GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_API_KEY"
# MODEL=gemini-2.5-flash
# EOF