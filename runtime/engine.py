"""Continuous batching loop with prefix dedup and chunked prefill."""
from __future__ import annotations

import time
from typing import Dict, List, Optional

from server.scheduler import RequestOrchestrator, Scheduler
from .kv import PagedKVAllocator
from .prefix_cache import PrefixCache


class FlashAttention:
    """Placeholder for a FlashAttention-backed kernel.

    The real implementation would call into a CUDA kernel; here we simply expose
    an interface to keep the scheduling logic testable.
    """

    def run(self, batch_tokens: List[List[int]]) -> List[List[float]]:  # pragma: no cover - illustrative
        return [[float(token) for token in seq] for seq in batch_tokens]


class ContinuousBatchEngine:
    def __init__(
        self,
        scheduler: Optional[Scheduler] = None,
        kv_allocator: Optional[PagedKVAllocator] = None,
        prefix_cache: Optional[PrefixCache] = None,
        prefill_chunk_size: int = 128,
    ) -> None:
        self.orchestrator = RequestOrchestrator(scheduler or Scheduler())
        self.kv = kv_allocator or PagedKVAllocator()
        self.prefix_cache = prefix_cache or PrefixCache()
        self.prefill_chunk_size = prefill_chunk_size
        self.flash_attention = FlashAttention()
        self.prefill_offsets: Dict[str, int] = {}

    def submit_request(self, request_id: str, tokens: List[int], lane: str = "default") -> None:
        self.orchestrator.submit(request_id, total_tokens=len(tokens), lane=lane)
        self.prefill_offsets[request_id] = 0
        entry = self.prefix_cache.upsert(request_id, tokens)
        # Pin the first block for shared prefix reuse
        self.kv.allocate(owner=entry.prefix_hash, kv_length=len(tokens), pin=True)

    def _chunk_tokens(self, tokens: List[int]) -> List[List[int]]:
        return [tokens[i : i + self.prefill_chunk_size] for i in range(0, len(tokens), self.prefill_chunk_size)]

    def _prefill(self, request_id: str, tokens: List[int]) -> None:
        chunks = self._chunk_tokens(tokens)
        for chunk in chunks:
            self.kv.allocate(owner=request_id, kv_length=len(chunk))
            self.orchestrator.tick(tokens_served=len(chunk))
            self.kv.touch(owner=request_id)

    def _reuse_prefix(self, request_id: str, tokens: List[int]) -> bool:
        entry = self.prefix_cache.match(tokens)
        if not entry:
            return False
        # Reuse cached blocks bound to the prefix hash instead of re-allocating
        owner_blocks = self.kv.describe_owner(entry.prefix_hash)
        if not owner_blocks:
            return False
        self.kv.touch(entry.prefix_hash)
        self.kv.allocate(owner=request_id, kv_length=len(tokens))
        return True

    def run_once(self, pending: Dict[str, List[int]]) -> Optional[str]:
        """Process a batch tick; returns the request_id served."""

        if not pending:
            return None

        # Attempt dedup first for all pending prefixes
        for request_id, tokens in pending.items():
            if self._reuse_prefix(request_id, tokens):
                self.orchestrator.tick(tokens_served=len(tokens))
                return request_id

        # Otherwise service the next scheduled request with chunked prefill
        scheduled = self.orchestrator.scheduler.next_request()
        if not scheduled:
            # bootstrap new requests
            request_id, tokens = next(iter(pending.items()))
            self.submit_request(request_id, tokens)
            scheduled = self.orchestrator.scheduler.next_request()
            if not scheduled:
                return None

        request_id = scheduled.request_id
        tokens = pending[request_id]
        self._prefill(request_id, tokens)
        self.orchestrator.complete(request_id)
        return request_id

    def attention_step(self, batch: List[List[int]]) -> List[List[float]]:
        """Run a FlashAttention-backed forward pass for the batch."""

        return self.flash_attention.run(batch)

    def stats(self) -> Dict[str, Dict[str, int]]:
        return {
            "kv": self.kv.get_cache_stats().__dict__,
            "prefix": self.prefix_cache.stats(),
        }
