"""
Nefesh MCP Server — Streamable HTTP Proxy
Copyright (c) 2026 Nefesh AI Ltd. All rights reserved.
Author: Tom Stuhl <Tom.Stuhl@nefesh.ai>

Stateless MCP proxy: forwards all tool calls to api.nefesh.ai.
Supports stdio (for registry inspection) and Streamable HTTP (production).
"""

from __future__ import annotations

import os
import json
from contextvars import ContextVar

import httpx
from mcp.server.fastmcp import FastMCP

# ── Config ──────────────────────────────────────────────────────
API_URL = os.environ.get("NEFESH_API_URL", "https://api.nefesh.ai")

# Context var: stores the caller's API key per-request
_nefesh_key: ContextVar[str] = ContextVar("nefesh_key", default="")


def _headers() -> dict:
    """Build proxy headers with the caller's API key."""
    key = _nefesh_key.get() or os.environ.get("NEFESH_API_KEY", "")
    return {"X-Nefesh-Key": key, "Content-Type": "application/json"}


# ── MCP Server ──────────────────────────────────────────────────
mcp = FastMCP(
    "nefesh",
    instructions=(
        "Human State Fusion — send any body signal, "
        "get a unified state for your LLM. "
        "Includes trigger memory for cross-session context. "
        "Not a medical device. Version 2.0.0."
    ),
)


# ── Tool: get_human_state ───────────────────────────────────────
@mcp.tool()
async def get_human_state(session_id: str) -> dict:
    """Get current unified human state for a session.

    Returns stress level (0-100), state label, active signals, confidence,
    and an LLM behavior recommendation. Call before generating important
    responses to adapt tone, length, and complexity. Not a medical device.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{API_URL}/v1/state",
            params={"session_id": session_id},
            headers=_headers(),
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"No data for session {session_id}. Send signals via ingest first."}


# ── Tool: ingest ────────────────────────────────────────────────
@mcp.tool()
async def ingest(
    session_id: str,
    timestamp: str,
    heart_rate: float | None = None,
    rmssd: float | None = None,
    sdnn: float | None = None,
    spo2: float | None = None,
    pnn50: float | None = None,
    mean_ibi: float | None = None,
    ibi_count: int | None = None,
    tone: str | None = None,
    speech_rate: float | None = None,
    pitch_variability: float | None = None,
    expression: str | None = None,
    gaze: str | None = None,
    posture: str | None = None,
    engagement: float | None = None,
    sentiment: float | None = None,
    urgency: str | None = None,
    glucose_mg_dl: float | None = None,
    glucose_mmol_l: float | None = None,
    glucose_trend: str | None = None,
    eeg_alpha_power: float | None = None,
    eeg_beta_power: float | None = None,
    eeg_theta_power: float | None = None,
    cognitive_load: float | None = None,
    eda: float | None = None,
    skin_temperature: float | None = None,
    respiratory_rate: float | None = None,
    steps_last_minute: int | None = None,
    activity_level: str | None = None,
    sleep_stage: str | None = None,
    stress_score: float | None = None,
    source_device: str | None = None,
    confidence: float | None = None,
    subject_id: str | None = None,
    user_message: str | None = None,
    ai_response: str | None = None,
) -> dict:
    """Send human signals from any sensor, get unified state back.

    session_id + timestamp + at least one signal required.
    Heart rate, glucose, EEG, voice tone, facial expression —
    send what you have. Include user_message + ai_response to
    activate Trigger Memory. Not a medical device.
    """
    payload = {k: v for k, v in locals().items() if v is not None}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{API_URL}/v1/ingest",
            json=payload,
            headers=_headers(),
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": "Signal processing failed. Check payload format."}


# ── Tool: get_trigger_memory ────────────────────────────────────
@mcp.tool()
async def get_trigger_memory(subject_id: str) -> dict:
    """Retrieve psychological trigger profile for a subject.

    Shows which conversation topics cause stress (active triggers)
    and which have been resolved. Requires subject_id from previous
    ingest calls with user_message + ai_response. Not a medical device.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{API_URL}/v1/triggers",
            params={"subject_id": subject_id},
            headers=_headers(),
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"No trigger data for subject {subject_id}."}


# ── Tool: get_session_history ───────────────────────────────────
@mcp.tool()
async def get_session_history(session_id: str, minutes: int = 5) -> dict:
    """Get state history for a session over time.

    Returns timestamped datapoints with stress scores, states,
    and heart rates. Useful for trend analysis. Not a medical device.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{API_URL}/v1/history",
            params={"session_id": session_id, "minutes": minutes},
            headers=_headers(),
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"No history for session {session_id}."}


# ── Tool: delete_subject ────────────────────────────────────────
@mcp.tool()
async def delete_subject(subject_id: str) -> dict:
    """Permanently delete all data for a subject_id.

    Cascading: removes all sessions, TriggerMemory, and stored signals.
    GDPR/BIPA compliant. Irreversible. Not a medical device.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.delete(
            f"{API_URL}/v1/subjects/{subject_id}",
            headers=_headers(),
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": "Deletion failed. Check the subject_id."}


# ── Run ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
