#!/bin/bash
source .venv/bin/activate
uvicorn main:app --reload --port 3333 --host 0.0.0.0 