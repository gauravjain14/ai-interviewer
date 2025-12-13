from runtime.engine import ContinuousBatchEngine


def test_engine_reuses_prefix_and_tracks_stats():
    engine = ContinuousBatchEngine(prefill_chunk_size=4)
    tokens = [1, 2, 3, 4, 5, 6]
    pending = {"req1": tokens.copy()}

    engine.submit_request("req1", tokens)
    served = engine.run_once(pending)
    assert served == "req1"

    # Submit another request with same prefix to hit dedup path
    pending = {"req2": tokens.copy()}
    engine.submit_request("req2", tokens)
    served = engine.run_once(pending)
    assert served == "req2"

    stats = engine.stats()
    assert stats["prefix"]["entries"] >= 1
    assert stats["kv"]["used_blocks"] >= 1
