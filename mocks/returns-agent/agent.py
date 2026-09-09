"""Nova Market returns desk - a small ADK agent exposed over the A2A protocol (mock).

Deployed to Cloud Run in Lab06. The Nova Assistant delegates return requests to it
through Agent Gateway, so participants can see agent-to-agent traffic being governed.
"""
import asyncio
import os
import random

import uvicorn
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent

_RETURNS: dict[str, dict] = {}


def start_return(order_id: str, reason: str) -> dict:
    """Open a return (RMA) for an order.

    Args:
        order_id: The Nova Market order id, e.g. NV-10042.
        reason: Why the customer returns the item (defective, wrong item, changed mind, other).

    Returns:
        A dictionary with 'status' ('success'), the new 'rma' number, the 'order_id' and 'next_steps' to relay to the customer.
    """
    rma = f"RMA-{random.randint(100000, 999999)}"
    _RETURNS[rma] = {"order_id": order_id.upper(), "reason": reason, "status": "label_sent"}
    return {"status": "success", "rma": rma, "order_id": order_id.upper(),
            "next_steps": "A prepaid return label was emailed. Drop the parcel at any PPL point within 14 days."}


def get_return_status(rma: str) -> dict:
    """Check the status of an existing return by its RMA number.

    Args:
        rma: The RMA number, e.g. RMA-123456.

    Returns:
        A dictionary with a 'status' key.
        'success': 'return' holds order_id, reason and the return status (e.g. label_sent).
        'not_found': no return has this RMA number.
    """
    r = _RETURNS.get(rma.upper())
    return {"status": "success", "return": r} if r else {"status": "not_found", "rma": rma}


root_agent = Agent(
    name="nova_returns_agent",
    model="gemini-3.8-flash",
    description="Handles product returns for Nova Market: opens RMAs and reports return status.",
    instruction=(
        "You are the Nova Market returns desk. Use start_return to open a return when given an order id and a reason; "
        "use get_return_status for follow-ups. Reply with the RMA number and the next steps. Be brief."
    ),
    tools=[start_return, get_return_status],
)

# Public URL advertised in the agent card (Cloud Run URLs are deterministic per project number).
# We build the card ourselves so the advertised URL has no explicit ":443" port - Agent Gateway
# matches registered destinations by exact hostname/URL.
_host = os.environ.get("A2A_HOST", "localhost")
_port = int(os.environ.get("PORT", "8080"))
_rpc_url = f"https://{_host}/" if _host != "localhost" else f"http://localhost:{_port}/"
_card = asyncio.run(AgentCardBuilder(agent=root_agent, rpc_url=_rpc_url).build())
a2a_app = to_a2a(root_agent, agent_card=_card, host=_host, port=_port)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=_port)
