FROM python:3.12-slim
# pytest lives in a root-only venv: only the run_tests tool (exec as root) can use it, not the agent's bash (user `agent`).
RUN python -m venv /opt/testenv && /opt/testenv/bin/pip install --no-cache-dir pytest==8.3.4 \
 && chmod -R go-rwx /opt/testenv \
 && useradd -m agent
WORKDIR /work
