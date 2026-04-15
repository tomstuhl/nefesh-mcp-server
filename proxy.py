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
    key = _nefesh_key.get()
    return {"X-Nefesh-Key": key, "Content-Type": "application/json"}


# ── MCP Server ──────────────────────────────────────────────────
mcp = FastMCP(
    "nefesh",
    instructions=(
        "Human State Fusion — send any body signal, "
        "get a unified state for your LLM. "
        "Includes trigger memory for cross-session context. "
        "Not a medical device. MCP + A2A native. Version 4.0.0."
    ),
)


# ── Tool: get_human_state ───────────────────────────────────────
@mcp.tool()
async def get_human_state(session_id: str) -> dict:
    """Get current unified human state for a session. Call this before generating important responses.

    Returns:
    - state: calm | relaxed | focused | stressed | acute_stress
    - stress_score: 0-100 (lower = calmer)
    - confidence: 0.0-1.0 (based on signal quality and device type)
    - suggested_action: maintain_engagement | simplify_and_focus | de-escalate_and_shorten | pause_and_ground
    - action_reason: human-readable explanation of why this action was suggested
    - adaptation_effectiveness (on 2nd+ call): shows whether your previous suggested_action actually reduced stress — contains previous_action, stress_delta, and effective boolean. Use this to self-improve.

    Use suggested_action to adapt your response: calm/relaxed = full complexity, focused = shorter and structured, stressed = max 2 sentences, acute_stress = one grounding sentence only.

    Requires a prior ingest call to have data. Not a medical device.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{API_URL}/v1/state",
            params={"session_id": session_id},
            headers=_headers(),
        )
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            return {"error": f"No data for session {session_id}. Send signals via ingest first."}
        return {"error": f"API returned {resp.status_code}. Check your API key and parameters."}


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
    """Send biometric signals from any sensor, get unified state back.

    Required: session_id + timestamp (ISO 8601) + at least one signal.
    Send whatever you have — the API fuses all signals into one state.

    Common signals (highest impact):
    - heart_rate (bpm, 30-220) + rmssd (ms) — cardiovascular
    - tone: calm | tense | anxious | hostile — vocal
    - sentiment: -1.0 to 1.0 — textual
    - expression: relaxed | neutral | tense — visual

    For trigger memory (cross-session psychological tracking):
    - Include subject_id (consistent per user, hashed)
    - Include user_message + ai_response to detect stress topics

    Returns same fields as get_human_state plus signals_received list and topics_detected.

    source_device is optional but improves confidence scoring. Not a medical device.
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
        return {"error": f"API returned {resp.status_code}. Check your API key and parameters."}


# ── Tool: get_trigger_memory ────────────────────────────────────
@mcp.tool()
async def get_trigger_memory(subject_id: str) -> dict:
    """Retrieve psychological trigger profile for a subject.

    Returns which conversation topics consistently cause stress (active triggers) and which have been resolved over time.

    - active triggers: topics where stress was elevated across multiple sessions. Tread carefully.
    - resolved triggers: topics where stress has decreased. Safe to explore deeper.

    Each trigger includes observation_count, avg_score, peak_score, and last_seen.

    Requires prior ingest calls with the same subject_id. Not a medical device.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{API_URL}/v1/triggers",
            params={"subject_id": subject_id},
            headers=_headers(),
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"No trigger data found for subject {subject_id}."}


# ── Tool: get_session_history ───────────────────────────────────
@mcp.tool()
async def get_session_history(session_id: str, minutes: int = 5) -> dict:
    """Get state history for a session over time.

    Returns timestamped datapoints with stress_score, state, and heart_rate for each observation.
    Includes an overall trend: rising | falling | stable.

    Use minutes parameter to control the lookback window (default: 5, max: 60).
    Useful for detecting stress patterns during a conversation. Not a medical device.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{API_URL}/v1/history",
            params={"session_id": session_id, "minutes": minutes},
            headers=_headers(),
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"No history found for session {session_id}."}


# ── Tool: request_api_key (no auth required) ──────────────────
@mcp.tool()
async def request_api_key(email: str) -> dict:
    """Request a free Nefesh API key. No existing key needed.

    IMPORTANT: You MUST ask the user for their real email address before
    calling this tool. Do NOT invent, guess, or generate an email address.
    The user will receive a verification link they must click to activate
    the key. Without clicking that link, no API key will be issued.
    Disposable or temporary email services are blocked.

    Example prompt to the user: "What is your email address? You will
    receive a verification link to activate your free API key."

    Flow: call this with the user's real email, then poll
    check_api_key_status every 10 seconds until status is 'ready'.

    Free tier: 1,000 API calls/month, no credit card required.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{API_URL}/v1/keys/request",
            json={"email": email},
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"API returned {resp.status_code}. Check your email address."}


# ── Tool: check_api_key_status (no auth required) ─────────────
@mcp.tool()
async def check_api_key_status(email: str) -> dict:
    """Check the status of a pending API key request.

    Use the exact same email the user provided to request_api_key.
    Poll this every 10 seconds. Once the user clicks the verification
    link in their inbox, status changes from 'pending' to 'ready'
    and the response includes the API key.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{API_URL}/v1/keys/status",
            params={"email": email},
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"No pending request found for {email}."}


# ── Run ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
