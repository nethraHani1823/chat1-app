# Chat app — a DevOps starter project

A tiny chat app you will run four different ways. The app itself barely
matters. What matters is that each stage teaches one piece of the
pipeline you'll see at work.

| Stage | You do this | You learn |
|---|---|---|
| 1 | Run it on your laptop | What "the app" actually is |
| 2 | Put it in Docker | Packaging, containers |
| 3 | Push to GitHub | CI, automated testing |
| 4 | Deploy it | Getting it in front of users |

Work through them in order. Don't skip ahead.

---

## What's in the folder

```
chat-app/
├── app.py                  the whole backend, ~90 lines
├── templates/
│   ├── index.html          the home page: picture, headline, name box
│   └── room.html           the chat room, plus the JavaScript that runs it
├── static/
│   ├── style.css           all the styling for both pages
│   └── signal.svg          the picture on the home page
├── test_app.py             the automated tests
├── requirements.txt        the list of Python packages needed
├── Dockerfile              the recipe for packaging the app
└── .github/workflows/ci.yml    the pipeline
```

Two rules Flask follows without being told: HTML goes in `templates/`,
and anything the browser downloads directly — images, CSS, JavaScript —
goes in `static/`. Put a file in the wrong folder and it won't be found.

**How a page reaches your screen:** you ask for `/`, `app.py` matches that
to the `index()` function, that function renders `templates/index.html`,
and the browser then comes back for `style.css` and `signal.svg` from
`static/`. Four separate requests for one page. Watch them happen in your
browser's Network tab (F12) — reading that tab is a real DevOps skill.

---

## Stage 1 — run it on your laptop

```bash
cd chat-app

# A virtual environment: a private folder of Python packages for this
# project only, so projects don't fight over versions.
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open http://localhost:5000, type a name, and enter the room.

Now open a second browser tab — or your phone on the same wi-fi, using your
laptop's IP address instead of `localhost` — and join with a different name.
Type in one and watch it appear in the other. That's two clients talking to
one server, which is the shape of nearly every system you will work on.

Then open http://localhost:5000/health — that's the endpoint monitoring
tools poll to check the app is alive.

Stop it with `Ctrl+C`. Start it again. **Your messages are gone.**

That's your first real lesson: this app keeps everything in memory. Restart
it and the data vanishes. Deciding what survives a restart — and what
doesn't — is a big part of the job.

### Run the tests

```bash
pip install pytest
pytest -v
```

Eleven tests, all passing. Now go break something on purpose: open `app.py`
and delete these two lines from `write_message`:

```python
    if not name or not text:
        return jsonify({"error": "A name and a message are both required."}), 400
```

Run `pytest` again and watch tests go red. Put the lines back.

That red test is the entire point of CI. A machine catches the mistake
before a user does.

---

## Stage 2 — put it in a container

Install Docker Desktop first, then:

```bash
docker build -t chat-app .        # follow the recipe in Dockerfile
docker run -p 5000:5000 chat-app  # start a container from that image
```

Same app at http://localhost:5000 — but join the room and look at the top
right. Where it said "on your laptop" it now shows a container ID. Different
machine, same behaviour. That value comes from the `HOSTNAME` environment
variable, which Docker sets for you; `app.py` just reads it.

Useful commands while it runs (open a second terminal):

```bash
docker ps               # what's running
docker logs <name>      # what is it printing
docker stop <name>      # stop it
```

**Why this matters:** you can hand that image to anyone and it runs
identically. No "works on my machine". This is the thing you'll ship.

---

## Stage 3 — automate it with a pipeline

```bash
git init
git add .
git commit -m "chat app"
```

Create an empty repo on GitHub, then follow the two push commands it shows
you.

Now open the **Actions** tab in your repo. The pipeline is already running —
`.github/workflows/ci.yml` was in what you pushed, and GitHub found it.

Watch it: tests run, then the image builds, then the container is started
and health-checked. Green means it worked.

**Now break it deliberately.** Change something so a test fails, commit,
push. Watch the run go red and the build get skipped. Read the log to find
which test failed and why.

That's the daily rhythm of the job: push, watch, read logs when it's red.

---

## Stage 4 — deploy it

Pick somewhere free: Render, Railway, or Fly.io. Connect your GitHub repo
and let it build from your Dockerfile. In a few minutes you get a public URL
you can send to someone.

Then look at the `deploy` job at the bottom of `ci.yml` — it's an empty
placeholder. Filling it in so a push automatically updates the live site is
your next exercise.

---

## Where to go after this

In rough order:

1. Add a real database (Postgres) so messages survive restarts
2. Add environment variables for config instead of hardcoding
3. Write the infrastructure in Terraform instead of clicking in a console
4. Add monitoring so you get alerted when `/health` stops answering
5. Only then look at Kubernetes

## Things worth knowing

- **Never commit secrets.** Passwords and API keys go in GitHub Secrets or
  environment variables, never in a file you push. This is the single
  fastest way for an intern to cause a real incident.
- `app.run()` is a development server. Production uses something like
  gunicorn instead. Fine for learning, wrong for real traffic.
- Message text is inserted with `textContent`, not `innerHTML`, so someone
  typing `<script>` gets it shown as plain text rather than run. That one
  choice is the difference between a chat app and a security hole.
- There is no login. Anyone can claim any name. Fine on your laptop, not
  fine on the public internet.
- Polling every 2 seconds is the simple approach. Real chat apps use
  WebSockets so the server can push instead of being asked. Worth reading
  about once this version makes sense to you.
