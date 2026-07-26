# Technical Decision Note: Dockerfile Design

**Module:** 4 — Task Tracker API
**Status:** Draft
**Scope:** Containerization of the FastAPI backend only

## 1. Context

The Task Tracker runs locally using uvicorn. Before this module, anyone
using it needed Python installed on their own machine to run it. We added
Docker so the app can run in a container instead — no local Python setup
required anymore.

Our CI pipeline runs the test suite, but it doesn't build or run the Docker
image. So while I've manually verified the image builds and runs correctly,
nothing automated checks that on every push.

## 2. Decision

I used a two-stage Dockerfile.

The builder stage installs the requirements into a virtual environment.

The runtime stage creates a non-root user called `app`, switches to it, and
runs the app on port 8000 as that user.

The Dockerfile's `COPY` instructions mean only the `app/` folder actually
gets copied into the image — not `frontend/`, `tests/`, `docs/`, or any
other files. `.dockerignore` additionally keeps things like `.git`, `.env`,
and virtual environments out of the build context in the first place. This
is a local dev image, not a production deployment: no auth, no database,
no hardening beyond running as non-root.

## 3. Alternatives Considered

- **Single-stage build** (install directly into the final image, no
  builder/runtime split): I rejected this because it would bake build
  tooling and pip's cache into the runtime image, instead of only the
  installed virtualenv actually needed to run the app.
- **`COPY . .` instead of `COPY app ./app`**: I rejected this too — copying
  only the `app/` package keeps `frontend/`, `tests/`, and `docs/` out of
  the image regardless of what `.dockerignore` contains.
- **`docker-compose.yml` for one-command build+run**: not something I set
  up. The README documents plain `docker build` / `docker run` instead,
  and I haven't evaluated whether compose would actually add value here.
- **Running as root in the container**: I rejected this — the Dockerfile
  explicitly creates and switches to a non-root `app` user before `CMD`,
  since running as root inside a container is a common, avoidable risk.

## 4. Trade-offs

I decided to use a two-stage build mainly to keep things lightweight. It
leaves out all the extra build tools and `pip` temporary files that aren't
actually needed to run the app. In the end, only the final "run" stage
matters for size, and my final image turned out to be around 282MB — which
felt pretty reasonable to me.

The biggest trade-off I'm not super comfortable with is that there's no
automated test checking if this Dockerfile stays working. I tested it by
hand multiple times and know it works fine right now. However, if someone
renames a file or tweaks an import later on, the Docker setup could break
without anyone noticing until someone tries building it manually again.
Since CI isn't testing this yet, that's a real issue to keep in mind.

I also tagged the base image as `python:3.11-slim` instead of locking it
down with a specific digest hash. This means the underlying python image
could technically get updated in the background between builds. For a
learning project like this, I'm okay taking that small risk, though I
definitely wouldn't do that for a production app people rely on.

**I would do this differently by** adding a `docker build` check straight
into the CI pipeline right from the start instead of relying on manual
testing. I had everything ready to set it up during the session, but I
skipped it — and looking back, that was a real slip-up in my process
rather than just a feature I ran out of time for.

## 5. Consequences

- Anyone can build and run the backend in a container with two commands
  (`docker build`, `docker run`) without installing Python locally.
- The container still has no persistence — tasks are stored in memory, so
  restarting the container loses all data, same as running locally.
- The container has no authentication and isn't configured for exposure
  beyond local port mapping (`-p 8000:8000`); it shouldn't be treated as
  internet-facing or production-ready.
- Because CI doesn't build the image, a change that breaks the Dockerfile
  (like a renamed module under `app/`) would only be caught by someone
  manually running `docker build`.
- The Python version mismatch between my local venv (3.12.10) and the
  Dockerfile/CI (3.11) carries over into this decision too — I haven't
  confirmed which version is actually the "correct" one for this course.

## 6. Open Questions

The biggest question on my mind is whether the "no Docker" rule in my
`CLAUDE.md` file is just outdated, or if I missed something about the
project scope. I figured it was outdated because the instructor's slides
explicitly asked for a Dockerfile, but I haven't updated `CLAUDE.md` yet to
match. Right now, my project docs kind of contradict each other, so I need
to go back and clean that up instead of leaving it as-is.

I'm also still a bit unsure whether we're supposed to target Python 3.11
or 3.12 for this course. My local machine ended up using Python 3.12
(mostly because of a setup issue I ran into earlier), while my Dockerfile
and CI setup are both on 3.11. Everything seems to run fine on both so
far, but I'm not 100% sure which version the instructor or autograder
actually expects.

Finally, I wonder if we need a `docker-compose.yml` file or a
`HEALTHCHECK` instruction for this module, or if a basic `docker build`
and `docker run` setup is all that's expected. I'm open to adding them,
but I'd want to double-check what level of detail is actually required
for grading before spending extra time on it!
