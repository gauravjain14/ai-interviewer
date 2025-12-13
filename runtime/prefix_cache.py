"""Prefix hashing and deduplication utilities."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class CachedPrefix:
    prefix_hash: str
    tokens: Tuple[int, ...]
    owners: List[str]


class PrefixCache:
    """Caches KV cache lines for shared prefixes.

    Prefixes are hashed to avoid storing large token lists in the index. Multiple
    owners can reuse the same cached KV allocation when the prefix matches.
    """

    def __init__(self) -> None:
        self._entries: Dict[str, CachedPrefix] = {}

    @staticmethod
    def _hash_tokens(tokens: List[int]) -> str:
        data = ",".join(map(str, tokens)).encode()
        return hashlib.sha256(data).hexdigest()

    def probe(self, tokens: List[int]) -> str:
        prefix_hash = self._hash_tokens(tokens)
        return prefix_hash

    def match(self, tokens: List[int]) -> CachedPrefix | None:
        prefix_hash = self._hash_tokens(tokens)
        return self._entries.get(prefix_hash)

    def upsert(self, owner: str, tokens: List[int]) -> CachedPrefix:
        prefix_hash = self._hash_tokens(tokens)
        entry = self._entries.get(prefix_hash)
        if entry:
            if owner not in entry.owners:
                entry.owners.append(owner)
        else:
            entry = CachedPrefix(prefix_hash=prefix_hash, tokens=tuple(tokens), owners=[owner])
            self._entries[prefix_hash] = entry
        return entry

    def detach(self, owner: str) -> None:
        stale_hashes = []
        for prefix_hash, entry in self._entries.items():
            if owner in entry.owners:
                entry.owners.remove(owner)
            if not entry.owners:
                stale_hashes.append(prefix_hash)
        for prefix_hash in stale_hashes:
            self._entries.pop(prefix_hash, None)

    def stats(self) -> Dict[str, int]:
        return {"entries": len(self._entries)}
