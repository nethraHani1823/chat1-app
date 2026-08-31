# A Dockerfile is a recipe. Each line is one step, run top to bottom.
# The result is an "image" - a frozen box containing your app and
# everything it needs to run.

# Step 1: start from a machine that already has Python on it.
# "slim" means a stripped-down version, so the box stays small.
FROM python:3.12-slim

# Step 2: work inside /app instead of the root of the filesystem.
WORKDIR /app

# Step 3: copy ONLY the dependency list, then install.
# Why not copy everything first? Docker caches each step. Dependencies
# change rarely, your code changes constantly. Doing it in this order
# means editing app.py doesn't force a reinstall of Flask every time.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: now copy the rest of the code in.
COPY . .

# Step 5: document which port the app listens on.
EXPOSE 5000

# Step 6: the command that runs when the container starts.
CMD ["python", "app.py"]
