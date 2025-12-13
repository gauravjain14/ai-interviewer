from runtime.kv import PagedKVAllocator


def test_allocator_reuses_blocks_before_new_page():
    allocator = PagedKVAllocator(page_size=1024, block_size=256, max_pages=1)
    blocks_a = allocator.allocate(owner="reqA", kv_length=256)
    allocator.release("reqA")
    blocks_b = allocator.allocate(owner="reqB", kv_length=256)
    assert blocks_a[0].block_id == blocks_b[0].block_id
    stats = allocator.get_cache_stats()
    assert stats.reused_blocks >= 2  # allocation + reuse


def test_allocator_evicts_when_full():
    allocator = PagedKVAllocator(page_size=512, block_size=256, max_pages=1)
    allocator.allocate(owner="reqA", kv_length=256)
    allocator.allocate(owner="reqB", kv_length=256)
    allocator.allocate(owner="reqC", kv_length=256)
    stats = allocator.get_cache_stats()
    assert stats.evicted_blocks >= 1
