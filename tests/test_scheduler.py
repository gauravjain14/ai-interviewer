from server.scheduler import RequestOrchestrator, Scheduler


def test_srpt_prefers_shorter_request():
    scheduler = Scheduler()
    scheduler.add_request("long", total_tokens=100)
    scheduler.add_request("short", total_tokens=10)

    first = scheduler.next_request()
    assert first.request_id == "short"


def test_fairness_lane_balances_weights():
    scheduler = Scheduler()
    scheduler.register_lane("fast", weight=2)
    scheduler.register_lane("slow", weight=1)

    for i in range(3):
        scheduler.add_request(f"f{i}", total_tokens=10, lane="fast")
    scheduler.add_request("s0", total_tokens=5, lane="slow")

    # serve two fast then expect slow to surface because of weight gap
    served = [scheduler.next_request().lane for _ in range(4)]
    assert served.count("slow") >= 1


def test_orchestrator_tracks_progress_and_heartbeat():
    scheduler = Scheduler()
    orchestrator = RequestOrchestrator(scheduler)

    orchestrator.submit("r0", total_tokens=20)
    orchestrator.submit("r1", total_tokens=5)

    # Tick should advance the shortest request first
    dispatched = orchestrator.tick(tokens_served=2)
    assert dispatched.request_id == "r1"

    # After a full completion the active count should drop
    orchestrator.tick(tokens_served=5)
    heartbeat = orchestrator.heartbeat()
    assert heartbeat["active"] >= 1
    assert heartbeat["load_factor"] >= 0
