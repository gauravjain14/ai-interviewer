"""A simple paged KV allocator with reuse and eviction.

This module models a KV cache with fixed-size blocks organized into pages. Blocks
can be reused once released; when capacity is exhausted the allocator evicts the
least recently used unpinned block.
"""
from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Tuple


@dataclass
class CacheStats:
    total_blocks: int
    used_blocks: int
    reused_blocks: int
    evicted_blocks: int
    hits: int
    misses: int


@dataclass
class CacheBlock:
    block_id: int
    page_id: int
    size: int
    last_used: float
    owner: Optional[str] = None
    pinned: bool = False


@dataclass
class Page:
    page_id: int
    capacity: int
    blocks: List[CacheBlock]


class PagedKVAllocator:
    def __init__(
        self,
        page_size: int = 4096,
        block_size: int = 512,
        max_pages: int = 8,
    ) -> None:
        if block_size > page_size:
            raise ValueError("block_size cannot exceed page_size")
        self.page_size = page_size
        self.block_size = block_size
        self.max_pages = max_pages

        self.pages: List[Page] = []
        self.free_blocks: Deque[CacheBlock] = deque()
        self.blocks_by_owner: Dict[str, List[CacheBlock]] = {}

        self.reused_blocks = 0
        self.evicted_blocks = 0
        self.hits = 0
        self.misses = 0

    def _create_page(self) -> Page:
        if len(self.pages) >= self.max_pages:
            raise MemoryError("KV cache is full; cannot create more pages")
        page_id = len(self.pages)
        blocks_per_page = self.page_size // self.block_size
        blocks = [
            CacheBlock(block_id=i, page_id=page_id, size=self.block_size, last_used=time.time())
            for i in range(blocks_per_page)
        ]
        page = Page(page_id=page_id, capacity=blocks_per_page, blocks=blocks)
        self.pages.append(page)
        self.free_blocks.extend(blocks)
        return page

    def _ensure_capacity(self, required_blocks: int) -> None:
        while len(self.free_blocks) < required_blocks:
            if len(self.pages) < self.max_pages:
                self._create_page()
            else:
                self._evict_block()

    def _evict_block(self) -> None:
        # Find LRU unpinned block
        candidates: List[CacheBlock] = [
            block for page in self.pages for block in page.blocks if not block.pinned and block.owner is not None
        ]
        if not candidates:
            raise MemoryError("No evictable blocks available")
        block = min(candidates, key=lambda b: b.last_used)
        owner_blocks = self.blocks_by_owner.get(block.owner, [])
        owner_blocks = [b for b in owner_blocks if b.block_id != block.block_id or b.page_id != block.page_id]
        if owner_blocks:
            self.blocks_by_owner[block.owner] = owner_blocks
        else:
            self.blocks_by_owner.pop(block.owner, None)
        block.owner = None
        block.last_used = time.time()
        self.evicted_blocks += 1
        self.free_blocks.append(block)

    def _reuse_block(self) -> CacheBlock:
        block = self.free_blocks.popleft()
        self.reused_blocks += 1
        block.last_used = time.time()
        block.owner = None
        block.pinned = False
        return block

    def allocate(self, owner: str, kv_length: int, pin: bool = False) -> List[CacheBlock]:
        required_blocks = math.ceil(kv_length / self.block_size)
        self._ensure_capacity(required_blocks)

        allocated: List[CacheBlock] = []
        for _ in range(required_blocks):
            block = self._reuse_block()
            block.owner = owner
            block.pinned = pin
            allocated.append(block)

        self.blocks_by_owner.setdefault(owner, []).extend(allocated)
        return allocated

    def touch(self, owner: str) -> None:
        blocks = self.blocks_by_owner.get(owner, [])
        if blocks:
            self.hits += 1
        else:
            self.misses += 1
        for block in blocks:
            block.last_used = time.time()

    def release(self, owner: str) -> None:
        blocks = self.blocks_by_owner.pop(owner, [])
        for block in blocks:
            block.owner = None
            block.pinned = False
            block.last_used = time.time()
            # Reinsert at the head so freshly released blocks are reused first
            self.free_blocks.appendleft(block)

    def get_cache_stats(self) -> CacheStats:
        total_blocks = len(self.pages) * (self.page_size // self.block_size)
        used_blocks = total_blocks - len(self.free_blocks)
        return CacheStats(
            total_blocks=total_blocks,
            used_blocks=used_blocks,
            reused_blocks=self.reused_blocks,
            evicted_blocks=self.evicted_blocks,
            hits=self.hits,
            misses=self.misses,
        )

    def describe_owner(self, owner: str) -> List[Tuple[int, int]]:
        return [(b.page_id, b.block_id) for b in self.blocks_by_owner.get(owner, [])]
