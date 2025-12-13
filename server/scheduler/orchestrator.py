"""Request orchestrator built on top of the SRPT fairness scheduler."""
from __future__ import annotations

import time
from typing import Dict, Optional

from .scheduler import ScheduledRequest, Scheduler


class RequestOrchestrator:
    """Coordinates ingress/egress of generation requests.

    The orchestrator tracks outstanding requests, hands them to the scheduler,
    and keeps lightweight accounting state to surface backpressure decisions.
    """

    def __init__(self, scheduler: Optional[Scheduler] = None) -> None:
        self.scheduler = scheduler or Scheduler()
        self.active: Dict[str, ScheduledRequest] = {}

    def submit(self, request_id: str, total_tokens: int, lane: str = "default") -> ScheduledRequest:
        scheduled = self.scheduler.add_request(request_id, total_tokens, lane=lane)
        self.active[request_id] = scheduled
        return scheduled

    def complete(self, request_id: str) -> None:
        self.active.pop(request_id, None)

    def tick(self, tokens_served: int) -> Optional[ScheduledRequest]:
        """Advance the scheduler once and return the dispatched request.

        ``tokens_served`` lets the orchestrator apply SRPT progress accounting so
        subsequent scheduling decisions can take the updated remaining time into
        account.
        """

        next_req = self.scheduler.next_request()
        if not next_req:
            return None
        next_req.mark_progress(tokens_served)
        if next_req.remaining_tokens <= 0:
            self.complete(next_req.request_id)
        else:
            self.active[next_req.request_id] = next_req
        return next_req

    def load_factor(self) -> float:
        """Return a simple proxy for load based on pending work."""

        pending_tokens = sum(req.remaining_tokens for req in self.active.values())
        return pending_tokens / max(len(self.active), 1)

    def heartbeat(self) -> Dict[str, float]:
        """Expose a monitoring-friendly snapshot."""

        return {
            "timestamp": time.time(),
            "active": len(self.active),
            "load_factor": self.load_factor(),
        }
