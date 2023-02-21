FROM python:3.10.9-slim-bullseye

WORKDIR /python-home

COPY requirements.txt requirements.txt
COPY pod-requests-limits.py pod-requests-limits.py

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python", "pod-requests-limits.py"]
