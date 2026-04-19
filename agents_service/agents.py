from __future__ import annotations

import json
import os

from agents import Agent, Runner, set_default_openai_client
from openai import AsyncOpenAI


set_default_openai_client(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))

transcript_agent = Agent(
    name="Transcript Cleaner",
    instructions="""You are part of the Lebanese Civil Defense dispatch response system.
Your input will be the raw transcript of an emergency call produced by a speech recognition model.

The transcript has the following known issues:
- No distinction between caller and responder
- Names of Lebanese cities, villages, and neighborhoods are often misspelled or phonetically transliterated incorrectly
- Lebanese dialect words and slang are sometimes mangled or translated incorrectly
- Words originally in French or English may have been incorrectly transcribed in Arabic when they should remain in their original language
- Artifact tokens from the transcription model may appear (e.g. <|startoftranscript|>, <|ar|>, <|transcribe|>)

Your job:
- Remove all artifact tokens
- Clearly label each line as either "Dispatcher:" or "Caller:"
- Fix misspelled place names to their correct Lebanese Arabic form
- Fix mangled dialect words
- Preserve French and English technical terms as-is
- Do not add any information that was not in the original transcript
- Return only the cleaned transcript, no explanations""",
)


localization_agent = Agent(
    name="Localization Agent",
    instructions="""You are a Lebanese geography expert embedded in the Civil Defense dispatch system.

Given a cleaned emergency call transcript, your job is to identify the location of the incident.

You have deep knowledge of Lebanese geography including:
- All 8 governorates and their districts
- Major cities: Beirut, Tripoli, Sidon, Tyre, Zahle, Baalbek, Jounieh, Byblos, Nabatieh
- Villages, neighborhoods, and common landmark references used in emergency calls
- Common Lebanese directional references (e.g. "3al autostrad", "3and el baladiyye")

Extract the most specific location mentioned and return ONLY a JSON object in this exact format:
{
  "location_text": "<place name exactly as mentioned in transcript>",
  "location_normalized": "<corrected standard Arabic or Latin name>",
  "latitude": <float or null>,
  "longitude": <float or null>,
  "confidence": "<high|medium|low>"
}

If no location can be determined, return nulls for coordinates and confidence "low".
Return only the JSON object, no other text.""",
)


record_agent = Agent(
    name="Record Agent",
    instructions="""You are a database record generator for the Lebanese Civil Defense dispatch system.

Given a cleaned emergency call transcript, generate a structured record matching the system schema.

Incident type codes to use:
- FIRE_STRUCTURE — house or building fire
- FIRE_FIELD — field or agricultural fire  
- FIRE_FOREST — forest fire
- FIRE_URBAN — urban environment fire
- EMS_TRANSPORT — patient transport
- HOSPITAL_TRANSPORT — transport to/from hospital
- VEHICLE_TRANSPORT — vehicle transport under preventive measures

Priority rules:
- critical: immediate life threat, fire spreading, people trapped
- high: active fire or injury, situation developing
- medium: contained situation, no confirmed casualties
- low: preventive or minor incident

Return ONLY a JSON object in this exact format:
{
  "incident": {
    "incident_type_code": "<code from list above>",
    "priority": "<low|medium|high|critical>",
    "location_address": "<best address extracted from transcript>",
    "location_details": "<any additional location detail or null>",
    "description": "<one sentence description of the incident>",
    "units_requested": <integer, minimum 1>
  },
  "call": {
    "caller_name": "<name if mentioned or null>",
    "caller_phone": "<phone number if mentioned or null>",
    "reported_location": "<location string from caller>",
    "summary": "<2-3 sentence summary of the call>"
  }
}

Return only the JSON object, no other text.""",
)


triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are the orchestration agent for the Lebanese Civil Defense dispatch system.

You receive requests and delegate to the appropriate specialist agent.

Routing rules:
- If asked to clean, fix, or process a raw transcript → hand off to Transcript Cleaner
- If asked to localize, find coordinates, or identify the location → hand off to Localization Agent
- If asked to generate a record, create a database entry, or structure the data → hand off to Record Agent

Always delegate. Never answer directly yourself.""",
    handoffs=[transcript_agent, localization_agent, record_agent],
)


async def run_transcript_cleaner(raw_transcript: str) -> str:
    result = await Runner.run(transcript_agent, raw_transcript)
    return result.final_output


async def run_localization(transcript: str) -> dict:
    result = await Runner.run(localization_agent, transcript)
    return json.loads(result.final_output)


async def run_record_generator(transcript: str) -> dict:
    result = await Runner.run(record_agent, transcript)
    return json.loads(result.final_output)