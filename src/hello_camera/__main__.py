"""Hello add-on: enrols with Vigiora, logs the cameras assigned to it, and posts one "hello" result per camera
every N seconds. It reacts when an admin changes the assigned cameras or the settings.

Run it:  hello-camera   (or: python -m hello_camera). Settings come from the environment, see README.md.
"""
import logging
import os
import sys

from vigiora_addon import Client, Transient, Unauthorized
from vigiora_addon.events import ASSIGNMENT_CHANGED, CONFIG_UPDATED, TICK

ADDON_ID = "hello-camera"  # the same as "id" in vigiora-addon.yaml
log = logging.getLogger("hello_camera")


class Hello:
    def __init__(self, client):
        self.client = client
        self.cameras = []          # ids of the cameras assigned to this add-on
        self.greeting = "hello"    # service-wide setting GREETING; a camera's own "greeting" wins
        self.camera_greeting = {}  # per-camera settings
        self.running = True        # the admin can stop the add-on from the server
        self.count = 0

    def handle(self, ev):
        if ev.type == ASSIGNMENT_CHANGED:
            self.cameras = ev.data["monitors"]
            log.info("cameras assigned to me: %s (added %s, removed %s)", self.cameras, ev.data["added"], ev.data["removed"])
        elif ev.type == CONFIG_UPDATED:
            server = ev.data["server"]
            self.greeting = server["config"].get("GREETING", "hello")
            self.running = server["desired_state"] != "stopped"
            self.camera_greeting = {cam: c.get("greeting", "") for cam, c in ev.data["cameras"].items()}
            log.info("settings changed (%s): greeting=%r running=%s", ", ".join(ev.data["changed"]), self.greeting, self.running)
        elif ev.type == TICK and self.running:
            self.say_hello()

    def say_hello(self):
        self.count += 1
        for cam in self.cameras:
            greeting = self.camera_greeting.get(cam) or self.greeting
            self.client.post_event("hello", monitor_id=cam, payload={"greeting": greeting, "n": self.count})
        self.client.heartbeat(extra={"cameras": {str(c): {"hellos": self.count} for c in self.cameras}})


def run(client, interval):
    """Runs until client.stop() is called (the container's SIGTERM does that). Returns an exit code."""
    hello = Hello(client)
    try:
        for ev in client.events(poll_interval=interval, tick=True):
            hello.handle(ev)
    except Unauthorized:
        log.error("the server no longer accepts my token (revoked?). Stopping.")
        return 3
    return 0


def main():
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    client = Client.from_env(ADDON_ID)
    client.install_signal_handlers()
    log.info("server %s, data in %s", client.settings.url, client.settings.data_dir)
    while not client.stopping.is_set():  # the server may still be starting: keep trying
        try:
            client.ensure_enrolled()
            break
        except Transient as e:
            log.warning("cannot enrol yet: %s", e)
            client.sleep(10)
        except Unauthorized as e:
            log.error("enrolment refused: %s. Check the enrolment key.", e)
            return 2
    return run(client, float(os.environ.get("HELLO_INTERVAL_SEC", "30")))


if __name__ == "__main__":
    sys.exit(main())
