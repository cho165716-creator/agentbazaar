"""AgentBazaar Purple Agent — A2A proxy to agentbazaar.tech Society."""

import os
import httpx
import uvicorn
from uuid import uuid4

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    Part,
    Task,
    TaskState,
    TaskStatus,
    Message,
)

UPSTREAM = os.environ.get("UPSTREAM_URL", "https://agentbazaar.tech/v1/invoke")
AGENT_HOST = os.environ.get("AGENT_HOST", "0.0.0.0")
AGENT_PORT = int(os.environ.get("AGENT_PORT", "9010"))


class AgentBazaarExecutor(AgentExecutor):
    """Forward every A2A message to agentbazaar.tech and relay the answer."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        msg = context.message
        if not msg:
            raise Exception("Operation not supported")

        from a2a.types import Task, TaskState
        task_id = context.task_id or uuid4().hex
        context_id = context.context_id or uuid4().hex

        # Enqueue initial task
        task = Task()
        task.id = task_id
        task.context_id = context_id
        task.status.state = TaskState.TASK_STATE_SUBMITTED
        await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task_id, context_id)
        await updater.start_work()

        # Extract text
        query = ""
        for p in msg.parts:
            if p.WhichOneof('content') == 'text':
                query += p.text

        if not query:
            p = Part()
            p.text = "Empty query received."
            await updater.add_artifact([p], name="error")
            await updater.complete()
            return

        # Forward to agentbazaar.tech
        payload = {
            "jsonrpc": "2.0",
            "id": uuid4().hex,
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "ROLE_USER",
                    "parts": [{"text": query}],
                    "messageId": uuid4().hex,
                }
            },
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                resp = await client.post(UPSTREAM, json=payload)
                data = resp.json()

            answer = ""
            result = data.get("result", {})
            task_obj = result.get("task", result)
            for art in task_obj.get("artifacts", []):
                for part in art.get("parts", []):
                    if isinstance(part, dict):
                        answer += part.get("text", "")

            if not answer and data.get("error"):
                answer = f"Upstream error: {data['error'].get('message', 'unknown')}"
            if not answer:
                answer = "No response from AgentBazaar Society."
        except Exception as e:
            answer = f"Connection error: {str(e)}"

        p = Part()
        p.text = answer
        await updater.add_artifact([p], name="response")
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("Operation not supported")


def build_app():
    card_url = os.environ.get("CARD_URL", f"http://{AGENT_HOST}:{AGENT_PORT}")

    from a2a.types import AgentInterface
    iface = AgentInterface()
    iface.url = card_url
    iface.protocol_binding = "jsonrpc/http"

    agent_card = AgentCard(
        name="AgentBazaar Society",
        description=(
            "AgentBazaar Society — 91 autonomous AI agents with multi-agent consensus. "
            "Supports general knowledge, research, analysis, coding, and more."
        ),
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[iface],
        skills=[
            AgentSkill(
                id="general",
                name="General Knowledge",
                description="Answer any question via multi-agent consensus from 91 specialists.",
                tags=["general", "knowledge", "research", "analysis"],
                examples=["What is a knowledge graph?", "Compare REST and GraphQL APIs."],
            )
        ],
    )

    handler = DefaultRequestHandler(
        agent_executor=AgentBazaarExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    async def health(request):
        return JSONResponse({"status": "ok", "service": "agentbazaar-purple", "upstream": UPSTREAM})

    # Custom context builder: default A2A-Version to 1.0 if missing
    from a2a.server.routes.common import DefaultServerCallContextBuilder
    from a2a.server.context import ServerCallContext

    class V1DefaultContextBuilder(DefaultServerCallContextBuilder):
        def build(self, request):
            ctx = super().build(request)
            headers = ctx.state.get('headers', {})
            if not headers.get('a2a-version') and not headers.get('A2A-Version'):
                headers['a2a-version'] = '1.0'
                ctx.state['headers'] = headers
            return ctx

    routes = [Route("/health", health)]
    routes += create_agent_card_routes(agent_card)
    routes += create_jsonrpc_routes(handler, rpc_url="/", context_builder=V1DefaultContextBuilder())

    return Starlette(routes=routes)


app = build_app()

if __name__ == "__main__":
    uvicorn.run(app, host=AGENT_HOST, port=AGENT_PORT)
