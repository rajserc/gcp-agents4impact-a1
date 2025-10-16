#DC_API_KEY 
#Z8nz7BNxMhgYAzuxovXh9eSCTdvKzo2Th17nFK7d2UILEjZ2
#Tx3ctQdiKUmDzDG2kDSJVdGVnhiMh8QxLVHLVA0GRm2AkVccpcZzE83sd2jMAmL

#googleapi key
#AIzaSyAhshHALo20t51K9E9CTeTUjvlmxkVpbmE

at << EOF > google_maps_mcp_agent/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-a7f3a921567b
GOOGLE_CLOUD_LOCATION=us-west1
GOOGLE_MAPS_API_KEY="AIzaSyC-2QMi2uhdsGiWweEfOoIFeq_1BU0G9lY"
MODEL=gemini-2.5-flash
EOF

gcloud storage cp -r gs://qwiklabs-gcp-00-192c721187b5-bucket/adk_multiagent_systems .

export PATH=$PATH:"/home/${USER}/.local/bin"
python3 -m pip install google-adk -r adk_multiagent_systems/requirements.txt

cd ~/adk_multiagent_systems
cat << EOF > parent_and_subagents/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-00-192c721187b5
GOOGLE_CLOUD_LOCATION=global
MODEL=gemini-2.5-flash
EOF

cp parent_and_subagents/.env workflow_agents/.env

sub_agents=[travel_brainstormer, attractions_planner]

cd ~/adk_multiagent_systems
adk run parent_and_subagents

def save_attractions_to_state(
    tool_context: ToolContext,
    attractions: List[str]
) -> dict[str, str]:
    """Saves the list of attractions to state["attractions"].

    Args:
        attractions [str]: a list of strings to add to the list of attractions

    Returns:
        None
    """
    # Load existing attractions from state. If none exist, start an empty list
    existing_attractions = tool_context.state.get("attractions", [])

    # Update the 'attractions' key with a combo of old and new lists.
    # When the tool is run, ADK will create an event and make
    # corresponding updates in the session's state.
    tool_context.state["attractions"] = existing_attractions + attractions

    # A best practice for tools is to return a status message in a return dict
    return {"status": "success"}


tools=[save_attractions_to_state]

adk web

critic = Agent(
    name="critic",
    model=model_name,
    description="Reviews the outline so that it can be improved.",
    instruction="""
    INSTRUCTIONS:
    Consider these questions about the PLOT_OUTLINE:
    - Does it meet a satisfying three-act cinematic structure?
    - Do the characters' struggles seem engaging?
    - Does it feel grounded in a real time period in history?
    - Does it sufficiently incorporate historical details from the RESEARCH?

    If the PLOT_OUTLINE does a good job with these questions, exit the writing loop with your 'exit_loop' tool.
    If significant improvements can be made, use the 'append_to_state' tool to add your feedback to the field 'CRITICAL_FEEDBACK'.
    Explain your decision and briefly summarize the feedback you have provided.

    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    RESEARCH:
    { research? }
    """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[append_to_state, exit_loop]
)

writers_room = LoopAgent(
    name="writers_room",
    description="Iterates through research and writing to improve a movie plot outline.",
    sub_agents=[
        researcher,
        screenwriter,
        critic
    ],
    max_iterations=5,
)

film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Write a film plot outline and save it as a text file.",
    sub_agents=[
        writers_room,
        file_writer
    ],
)

box_office_researcher = Agent(
    name="box_office_researcher",
    model=model_name,
    description="Considers the box office potential of this film",
    instruction="""
    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    INSTRUCTIONS:
    Write a report on the box office potential of a movie like that described in PLOT_OUTLINE based on the reported box office performance of other recent films.
    """,
    output_key="box_office_report"
)

casting_agent = Agent(
    name="casting_agent",
    model=model_name,
    description="Generates casting ideas for this film",
    instruction="""
    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    INSTRUCTIONS:
    Generate ideas for casting for the characters described in PLOT_OUTLINE
    by suggesting actors who have received positive feedback from critics and/or
    fans when they have played similar roles.
    """,
    output_key="casting_report"
)

preproduction_team = ParallelAgent(
    name="preproduction_team",
    sub_agents=[
        box_office_researcher,
        casting_agent
    ]
)


#call mcp

import os
import sys
import logging

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv
import google.cloud.logging
from google.adk import Agent
from google.genai import types
from typing import Optional, List, Dict

from google.adk.tools.tool_context import ToolContext

load_dotenv()

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

# Tools (add the tool here when instructed)


# Agents

attractions_planner = Agent(
    name="attractions_planner",
    model=os.getenv("MODEL"),
    description="Build a list of attractions to visit in a country.",
    instruction="""
        - Provide the user options for attractions to visit within their selected country.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # When instructed to do so, paste the tools parameter below this line

    )

travel_brainstormer = Agent(
    name="travel_brainstormer",
    model=os.getenv("MODEL"),
    description="Help a user decide what country to visit.",
    instruction="""
        Provide a few suggestions of popular countries for travelers.
        
        Help a user identify their primary goals of travel:
        adventure, leisure, learning, shopping, or viewing art

        Identify countries that would make great destinations
        based on their priorities.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

root_agent = Agent(
    name="steering",
    model=os.getenv("MODEL"),
    description="Start a user on a travel adventure.",
    instruction="""
        Ask the user if they know where they'd like to travel
        or if they need some help deciding.
        """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    # Add the sub_agents parameter when instructed below this line

)
