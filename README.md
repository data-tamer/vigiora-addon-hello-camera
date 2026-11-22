# Hello Camera

A small, complete Vigiora add-on. Copy it, rename it, and put your own logic in `src/`.

It enrols with a Vigiora server, logs the cameras an admin assigned to it, and posts one harmless `hello` result per camera every 30 seconds. It reacts at once when the assigned cameras or its settings change. It is about 80 lines (`src/hello_camera/__main__.py`) and is built on the [Vigiora Add-on Kit](https://github.com/data-tamer/vigiora-addon-kit).

The text you are reading is the long description the Vigiora Community shows on your add-on's page. Replace it with yours. `docs/how-to.md` is the set-up guide.

![Placeholder screenshot](images/screenshot-1.png)

## What is in this repository

| Path | What it is |
|---|---|
| `vigiora-addon.yaml` | The manifest: name, version, hardware, permissions, how it runs. Commented. |
| `compose.yaml` | How Vigiora runs it. Checked against the manifest. |
| `Dockerfile` | Built on the server from this repository (`run.source: build`). |
| `src/hello_camera/__main__.py` | The add-on. |
| `tests/` | Tests that run the add-on against the kit's fake Vigiora server. |
| `docs/how-to.md` | Set-up and use guide (required). |
| `images/icon.png` | 256 x 256 icon (required). Drawn by `tools/make_images.py`. |
| `images/screenshot-1.png` | A placeholder screenshot. Replace it. |
| `compose.local.yaml` | For trying it with Docker on your own machine. The cloud does not read it. |
| `LICENSE` | Apache-2.0. Pick your own licence and change `licence:` in the manifest to match. |

## Make it yours

1. Pick an id. Run `vigiora-addon new my-addon` to get a copy with the names changed, or change them by hand: `id` and `name` in the manifest, `ADDON_ID` in `__main__.py`, `VIGIORA_ADDON_SERVICE_NAME` in `compose.yaml`, the package folder under `src/`.
2. Write your logic in `Hello.handle` and `Hello.say_hello`.
3. Ask only for the permissions you use (`permissions.scopes`).
4. Replace the icon, the screenshot, this README and the how-to.

## Test it locally

You need Python 3.10 or newer. The kit is not on a package index yet, so install it from a checkout first.

```sh
git clone https://github.com/data-tamer/vigiora-addon-kit ../vigiora-addon-kit   # or use your own checkout
python3 -m venv .venv && . .venv/bin/activate
pip install -e ../vigiora-addon-kit
pip install -e '.[dev]'

pytest                          # runs the add-on against the kit's fake Vigiora server
vigiora-addon validate .        # the same checks the Vigiora cloud runs when you submit
```

To watch it work by hand, use two terminals:

```sh
# terminal 1: a fake server. It prints the environment to use.
vigiora-addon run-fake --cameras 2 --service hello-camera

# terminal 2: paste the export lines it printed, then
HELLO_INTERVAL_SEC=3 hello-camera
```

Terminal 1 prints each result the add-on posts.

To try it in Docker against a real Vigiora server:

```sh
mkdir -p secrets && printf '<enrolment key>' > secrets/enroll_key
# edit VIGIORA_URL in compose.local.yaml, and set KIT_SOURCE in the Dockerfile
docker compose -f compose.yaml -f compose.local.yaml up --build
```

Then assign cameras to `hello-camera` on the server's HAL page. To build before the kit has a public address, pass a place to get it from: `docker compose build --build-arg KIT_SOURCE=<url of a kit tarball or wheel>` (or `docker build --build-arg KIT_SOURCE=...`).

## How the server starts it

Two things reach the add-on from outside, and the author cannot know either:

- the server's address, in `VIGIORA_URL`;
- the enrolment key, as a file at `/run/secrets/enroll_key` (the add-on reads `HAL_ENROLL_KEY_FILE`).

These are the same two things Vigiora Server 1.7.0 gives its own runners today. For those runners the server writes a compose file with the address spliced in as plain text, writes the key to `secrets/enroll_key` next to it (mode 600), and runs `docker compose up`. No `$` variable is involved, so the cloud's "no `$` in the compose file" rule does not get in the way.

Today the server does not yet install a compose file taken from an add-on repository. That is planned. `compose.yaml` already declares the key file mount (`./secrets/enroll_key`, a relative path, which the rules allow) and the environment names, and leaves out only `VIGIORA_URL`. How the server will add `VIGIORA_URL` to a compose file it did not write is not decided yet. Do not put a `$` variable in `compose.yaml` to get around it: the cloud refuses the submission.

## Before you submit

The cloud runs the same checks as `vigiora-addon validate .`. These are the rules that command cannot check, or that people forget.

- [ ] `vigiora-addon validate .` says OK, and `pytest` passes.
- [ ] **The id is yours to use.** It is 3 to 40 characters and never changes. These are reserved for Vigiora and refused: `objects`, `plates`, `faces`, `vision`, `core-ai`, `guardian`, `vigiora`, and anything starting with `vigiora-`, `hal-` or `official-`. An id belongs to the account that registers it first.
- [ ] **The version is higher** than your last approved version (semantic version, for example `0.1.0` then `0.1.1`). A rejected version number may be submitted again.
- [ ] **Images are pinned or built.** With `run.source: image`, every image in the compose file is listed in `run.images` and pinned by digest (`@sha256:` and 64 hex characters). With `run.source: build`, the compose file has a `build:` section, any other image is pinned, and the Dockerfile's `FROM` should be pinned by digest too.
- [ ] **The compose file is plain.** No `$` anywhere (write `$$` for a real dollar sign), no Docker socket, no `pid`, `ipc` or `userns_mode: host`, no mount of `/`, `/var/run`, `/run`, `/var/lib/docker`, `/proc`, `/sys`, `/etc` or `/dev`. `network_mode: host` only with `run.network: host`. `privileged`, `cap_add`, `devices`, `security_opt` and `volumes_from` only with `run.privileged: true`, and the reviewer looks at those closely.
- [ ] **Permissions are the least you need.** The administrator sees them before turning the add-on on.
- [ ] **How the commit is resolved.** You give the cloud a repository address (a public github.com or gitlab.com address over HTTPS) and, if you like, a branch or tag. The cloud resolves it to a commit itself, at preview and again at submit, and reviews that snapshot. A full 40-character commit hash is accepted only when it is on the default branch. Push your final changes first, then submit.
- [ ] README and how-to are written for the people who will install it. Images in them come only from your `images/` folder.
- [ ] The icon is a square PNG, 128 to 512 pixels, at most 200 KB. Screenshots (up to 6) are PNG, JPEG or WebP, at most 500 KB and 2000 pixels on the longest side.
- [ ] `LICENSE` matches `licence:` in the manifest.
