"""Runs the add-on against the kit's fake Vigiora server. The fixtures come from vigiora-addon-kit (a pytest plugin)."""
import threading

import pytest

from hello_camera.__main__ import run


@pytest.fixture
def running(addon_client):
    """The add-on, running in a thread against the fake server, polling every 50 ms."""
    t = threading.Thread(target=run, args=(addon_client, 0.05), daemon=True)
    t.start()
    yield addon_client
    addon_client.stop()
    t.join(timeout=5)
    assert not t.is_alive()


def hellos(fake):
    return [(e["body"]["monitor_id"], e["body"]["payload"]["greeting"]) for e in fake.events]


def test_posts_one_hello_per_assigned_camera(fake_vigiora, running):
    assert fake_vigiora.wait_for_events(4)
    first = fake_vigiora.events[:2]
    assert sorted(e["body"]["monitor_id"] for e in first) == [1, 2]
    assert all(e["body"]["label"] == "hello" for e in fake_vigiora.events)
    assert all(e["service_name"] == "test-addon" for e in fake_vigiora.events)


def test_sends_a_heartbeat(fake_vigiora, running):
    assert fake_vigiora.wait_for(lambda f: len(f.metrics) >= 1)
    assert "uptime_sec" in fake_vigiora.metrics[0]["body"]


def test_follows_a_new_camera(fake_vigiora, running):
    assert fake_vigiora.wait_for_events(2)
    fake_vigiora.add_camera(3)
    fake_vigiora.assign([1, 2, 3])
    assert fake_vigiora.wait_for(lambda f: any(c == 3 for c, _ in hellos(f)))


def test_stops_posting_for_a_removed_camera(fake_vigiora, running):
    assert fake_vigiora.wait_for_events(2)
    fake_vigiora.assign([1])
    assert fake_vigiora.wait_for(lambda f: [c for c, _ in hellos(f)[-3:]] == [1, 1, 1])


def test_uses_the_greeting_setting(fake_vigiora, running):
    fake_vigiora.set_config(GREETING="ciao")
    assert fake_vigiora.wait_for(lambda f: any(g == "ciao" for _, g in hellos(f)))


def test_a_camera_setting_wins(fake_vigiora, running):
    fake_vigiora.set_config(GREETING="ciao")
    fake_vigiora.set_camera_config(2, greeting="hola")
    assert fake_vigiora.wait_for(lambda f: (2, "hola") in hellos(f) and (1, "ciao") in hellos(f))


def test_pauses_when_the_admin_stops_it(fake_vigiora, running):
    assert fake_vigiora.wait_for_events(2)
    fake_vigiora.set_desired_state("stopped")
    fake_vigiora.wait_for(lambda f: False, timeout=0.4)  # let the change arrive and any post in flight finish
    n = len(fake_vigiora.events)
    fake_vigiora.wait_for(lambda f: False, timeout=0.5)
    assert len(fake_vigiora.events) == n
    fake_vigiora.set_desired_state("running")
    assert fake_vigiora.wait_for(lambda f: len(f.events) > n)
