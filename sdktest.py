from pranthora import Pranthora

client = Pranthora(api_key="a967a994b2ee02c0b4578e5e02bba7d3", base_url="http://localhost:5050/api/v1")

# # Create an agent with default configurations
# agent = client.agents.create(
#     name="Raj's Assistant",
#     description="Raj's voice assistant",
#     model="gemini-2.5-flash-lite",
#     voice="priya",
#     transcriber="deepgram_flux",
#     first_response_message="Hello! I am Raj",
#     system_prompt="You are RAJ a helpful assistant that can answer questions and help with tasks."
# )

# print(f"Created agent: {agent}")


# # Get all agents for the current user
# agents = client.agents.list()

# for agent in agents:
#     agent_data = agent.get('agent', {})
#     print(f"Name: {agent_data.get('name')}, ID: {agent_data.get('id')}")



# # Get a specific agent by ID
# agent = client.agents.get(agent_id="71f6a4be-7131-4b0e-8a4d-dae6db40850a")

# print(f"Agent: {agent}")


# # Update with configuration changes
# updated_agent = client.agents.update(
#     agent_id="71f6a4be-7131-4b0e-8a4d-dae6db40850a",
#     name="its anuj",
#     voice="apollo",
#     temperature=0.8,
#     model="gemini-2.5-flash-lite",
#     system_prompt="You are a AAANUJJJ helpful customer support agent."
# )

# print(f"Updated agent: {updated_agent}")



# # Or explicitly set force_delete
# client.agents.delete(agent_id="71f6a4be-7131-4b0e-8a4d-dae6db40850a", force_delete=True)

# Real-time voice: start outbound call (uses your attached phone number to call to_phone_number with the given agent)
# Replace +1234567890 with the number to call, and +0987654321 with your phone number

# Example 3: Outbound call with Elison provider
# print("\nStarting outbound call with Elison provider...")
# result_elison = client.start(
#     to_phone_number="9687579434",
#     from_number="+919484954320",  # Your Elison phone number
#     provider="elison"
# )
# print(f"Call started with Elison: {result_elison}")

# Example 4: Start multiple simultaneous calls
print("\nStarting multiple simultaneous calls...")
call_configs = [
    {
        "to_phone_number": "7405835650",
        "from_number": "+919484954309",
        "provider": "elison"
    },
    {
        "to_phone_number": "9687579434",  # Replace with another phone number
        "from_number": "+919484954309",
        "provider": "elison"
    }
]

results = client.start_multiple(call_configs=call_configs)
print(f"Multiple calls started: {results}")

# Optional: stop all calls
# stop_details = [
#     {"call_sid": result.get("call_sid"), "from_phone_number": result.get("from_phone_number")}
#     for result in results if "call_sid" in result
# ]
# stop_results = client.stop_multiple(call_details=stop_details)
# print(f"Multiple calls stopped: {stop_results}")