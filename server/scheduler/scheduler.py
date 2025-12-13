"""SRPT scheduler with fairness lanes for orchestrating inference requests.

The scheduler keeps per-lane queues and applies shortest-remaining-processing-time
(SRPT) ordering within each lane. It then chooses which lane to serve based on a
normalized service ratio so that heavier-weight lanes do not starve lighter ones.
"""
from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(order=True)
class ScheduledRequest:
    """A request scheduled by remaining token budget.

    The ordering is defined by (remaining_tokens, arrival_time) so the heap can
    always pop the shortest remaining job first (SRPT).
    """

    sort_index: Tuple[int, float] = field(init=False, repr=False)
    request_id: str
    total_tokens: int
    processed_tokens: int = 0
    arrival_time: float = field(default_factory=time.time)
    lane: str = "default"
    metadata: Optional[dict] = None

    def __post_init__(self) -> None:
        self.sort_index = (self.remaining_tokens, self.arrival_time)

    @property
    def remaining_tokens(self) -> int:
        return max(self.total_tokens - self.processed_tokens, 0)

    def mark_progress(self, tokens: int) -> None:
        self.processed_tokens += tokens
        self.sort_index = (self.remaining_tokens, self.arrival_time)


class FairnessLane:
    """A lane groups similar requests and tracks service share.

    The ``weight`` controls how often the lane can be picked relative to the
    others. A lane with weight=2 is expected to be served roughly twice as often
    as a lane with weight=1 when both have runnable requests.
    """

    def __init__(self, name: str, weight: float = 1.0) -> None:
        if weight <= 0:
            raise ValueError("Lane weight must be positive")
        self.name = name
        self.weight = weight
        self._served_tokens: int = 0
        self._queue: List[ScheduledRequest] = []

    @property
    def demand(self) -> float:
        """Return the normalized demand used for fairness selection."""

        if not self.weight:
            return float("inf")
        return self._served_tokens / self.weight

    @property
    def has_work(self) -> bool:
        return bool(self._queue)

    def push(self, request: ScheduledRequest) -> None:
        heapq.heappush(self._queue, request)

    def pop(self) -> ScheduledRequest:
        request = heapq.heappop(self._queue)
        return request

    def record_service(self, tokens: int) -> None:
        self._served_tokens += tokens

    def arrival_head_time(self) -> float:
        if not self._queue:
            return float("inf")
        return self._queue[0].arrival_time

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._queue)


class Scheduler:
    """SRPT scheduler with fairness lanes.

    The scheduler exposes ``add_request`` and ``next_request``. It prioritizes
    shorter remaining work while preventing large lanes from starving lighter
    ones by comparing per-lane normalized service.
    """

    def __init__(self, default_lane_weight: float = 1.0) -> None:
        self.lanes: Dict[str, FairnessLane] = {}
        self.default_lane_weight = default_lane_weight

    def register_lane(self, name: str, weight: Optional[float] = None) -> None:
        if name in self.lanes:
            return
        self.lanes[name] = FairnessLane(name, weight or self.default_lane_weight)

    def add_request(
        self,
        request_id: str,
        total_tokens: int,
        lane: str = "default",
        metadata: Optional[dict] = None,
    ) -> ScheduledRequest:
        if lane not in self.lanes:
            self.register_lane(lane)
        req = ScheduledRequest(request_id, total_tokens, lane=lane, metadata=metadata)
        self.lanes[lane].push(req)
        return req

    def update_progress(self, request_id: str, tokens: int) -> None:
        for lane in self.lanes.values():
            for item in lane._queue:
                if item.request_id == request_id:
                    item.mark_progress(tokens)
                    heapq.heapify(lane._queue)
                    return
        raise KeyError(f"Request {request_id} not found in scheduler")

    def pending(self) -> Iterable[ScheduledRequest]:
        for lane in self.lanes.values():
            yield from lane._queue

    def _eligible_lanes(self) -> List[FairnessLane]:
        return [lane for lane in self.lanes.values() if lane.has_work]

    def next_request(self) -> Optional[ScheduledRequest]:
        """Pick the next request following SRPT + fairness.

        Selection happens in two stages:
        1) Choose the lane with the lowest normalized service (served/weight).
        2) Within that lane, pop the shortest remaining job.
        """

        eligible = self._eligible_lanes()
        if not eligible:
            return None

        lane = min(eligible, key=lambda l: (l.demand, l.arrival_head_time()))
        next_req = lane.pop()
        lane.record_service(next_req.remaining_tokens)
        return next_req

    def snapshot(self) -> Dict[str, List[Tuple[str, int]]]:
        """Return a lightweight view for debugging/testing."""

        return {
            lane.name: [(req.request_id, req.remaining_tokens) for req in lane._queue]
            for lane in self.lanes.values()
        }


