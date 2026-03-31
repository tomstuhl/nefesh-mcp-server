# Nefesh MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that gives AI agents real-time awareness of human physiological state — stress level, confidence, and machine-readable behavioral actions.

## What it does

Your AI agent sends sensor data (heart rate, voice, video, text) via the Nefesh API. The MCP server returns a unified stress score (0-100), a state label (Calm → Acute Stress), a `suggested_action` your agent can follow directly, an `action_reason` explaining why, and `adaptation_effectiveness` showing whether the previous action actually worked.

**Zero prompt engineering required.** The agent gets a machine-readable action (`de-escalate_and_shorten`, `pause_and_ground`, etc.) and adapts automatically. On the 2nd+ call, the agent learns whether its previous approach reduced stress — a closed-loop feedback system.

**Signals supported:** cardiovascular (HR, HRV, RR intervals), vocal (pitch, jitter, shimmer), visual (facial action units), textual (sentiment, keywords)

## Setup

### 1. Get an API key

**Option A: Sign up manually**

Get a free key at [nefesh.ai/signup](https://nefesh.ai/signup) — 1,000 API calls/month, no credit card required.

**Option B: Let your AI agent get one automatically**

Your agent can self-provision a free API key via MCP — no manual signup needed. See [API Key Self-Provisioning](#api-key-self-provisioning) below.

Need more? [Solo plan](https://nefesh.ai/pricing) at $25/month for 50,000 calls.

### 2. Add to your AI agent

Find your agent's MCP config file:

| Agent | Config file |
|-------|-------------|
| **Cursor** | `~/.cursor/mcp.json` |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Code** | `.mcp.json` (project root) |
| **VS Code (Copilot)** | `.vscode/mcp.json` or `~/Library/Application Support/Code/User/mcp.json` |
| **Cline** | `cline_mcp_settings.json` (via UI: "Configure MCP Servers") |
| **Continue.dev** | `.continue/config.yaml` |
| **Roo Code** | `.roo/mcp.json` |
| **Amazon Q** | `~/.aws/amazonq/mcp.json` |
| **JetBrains IDEs** | Settings → Tools → MCP Server |
| **Zed** | `~/.config/zed/settings.json` (uses `context_servers`) |
| **OpenAI Codex CLI** | `~/.codex/config.toml` |
| **Goose CLI** | `~/.config/goose/config.yaml` |
| **ChatGPT Desktop** | Settings → Apps → Add MCP Server (UI) |
| **Gemini CLI** | Settings (UI) |
| **Augment** | Settings Panel (UI) |
| **Replit** | Integrations Page (web UI) |
| **LibreChat** | `librechat.yaml` (self-hosted) |

Add the following configuration (works with most agents):

```json
{
  "mcpServers": {
    "nefesh": {
      "url": "https://mcp.nefesh.ai/mcp",
      "headers": {
        "X-Nefesh-Key": "<YOUR_API_KEY>"
      }
    }
  }
}
```

<details>
<summary><strong>VS Code (Copilot)</strong> — uses <code>servers</code> instead of <code>mcpServers</code></summary>

```json
{
  "servers": {
    "nefesh": {
      "type": "http",
      "url": "https://mcp.nefesh.ai/mcp",
      "headers": {
        "X-Nefesh-Key": "<YOUR_API_KEY>"
      }
    }
  }
}
```
</details>

<details>
<summary><strong>Zed</strong> — uses <code>context_servers</code> in settings.json</summary>

```json
{
  "context_servers": {
    "nefesh": {
      "settings": {
        "url": "https://mcp.nefesh.ai/mcp",
        "headers": {
          "X-Nefesh-Key": "<YOUR_API_KEY>"
        }
      }
    }
  }
}
```
</details>

<details>
<summary><strong>OpenAI Codex CLI</strong> — uses TOML in <code>~/.codex/config.toml</code></summary>

```toml
[mcp_servers.nefesh]
url = "https://mcp.nefesh.ai/mcp"
```
</details>

<details>
<summary><strong>Continue.dev</strong> — uses YAML in <code>.continue/config.yaml</code></summary>

```yaml
mcpServers:
  - name: nefesh
    type: streamable-http
    url: https://mcp.nefesh.ai/mcp
```
</details>

All agents connect via [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) — no local installation required.

## Tools

| Tool | Description |
|------|-------------|
| `get_human_state` | Returns current stress state, score (0-100), confidence, `suggested_action`, and `action_reason` for a session |
| `ingest` | Send biometric signals — heart rate, voice tone, facial expression, sentiment, and 50+ more fields. Returns state + action + adaptation feedback. |
| `get_trigger_memory` | Returns psychological trigger profile — which topics cause stress, active vs. resolved |
| `get_session_history` | Returns chronological state history for a session |
| `delete_subject` | Deletes all stored data for a subject (GDPR compliance) |
| `request_api_key` | Request a free API key by email. Sends a verification link. No API key needed to call this tool. |
| `check_api_key_status` | Poll for API key activation after calling `request_api_key`. Returns the key once the email link is clicked. No API key needed. |

## Agent Actions

Every API response includes a `suggested_action` your agent can follow directly — no prompt engineering needed:

| Score | State | `suggested_action` | What the agent should do |
|-------|-------|-------------------|--------------------------|
| 0-19 | Calm | `maintain_engagement` | Full complexity. Challenge assumptions, push deeper. |
| 20-39 | Relaxed | `maintain_engagement` | Maintain complexity. 3-5 sentences. |
| 40-59 | Focused | `simplify_and_focus` | Reduce complexity. 2-3 sentences. Actionable. |
| 60-79 | Stressed | `de-escalate_and_shorten` | Max 2 sentences. Direct, factual, no ambiguity. |
| 80-100 | Acute Stress | `pause_and_ground` | Max 1 sentence. Single directive only. |

Example response (first call):
```json
{
  "state": "stressed",
  "stress_score": 73,
  "confidence": 0.87,
  "signals_received": ["cardiovascular", "vocal", "textual"],
  "suggested_action": "de-escalate_and_shorten",
  "action_reason": "elevated heart rate + anxious vocal tone + negative sentiment",
  "recommendation": "Max 2 sentences. Direct, factual, no ambiguity.",
  "disclaimer": "Not a medical device. For contextual AI adaptation only."
}
```

Inject it into your system prompt in one line:
```
ACTION: {suggested_action} — REASON: {action_reason}
```

## Adaptation Feedback Loop

On the 2nd+ call within the same session, the response includes `adaptation_effectiveness` — a closed-loop feedback mechanism that tells your agent whether the previous action actually reduced stress.

```json
{
  "state": "relaxed",
  "stress_score": 28,
  "confidence": 0.72,
  "signals_received": ["cardiovascular", "vocal"],
  "suggested_action": "maintain_engagement",
  "action_reason": "heart rate signal + calm vocal tone",
  "recommendation": "Maintain complexity. 3-5 sentences.",
  "disclaimer": "Not a medical device. For contextual AI adaptation only.",
  "adaptation_effectiveness": {
    "previous_action": "de-escalate_and_shorten",
    "previous_score": 73,
    "current_score": 28,
    "stress_delta": -45,
    "effective": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `previous_action` | string | The `suggested_action` from the previous call |
| `previous_score` | integer | Stress score from the previous call |
| `current_score` | integer | Stress score from this call |
| `stress_delta` | integer | Change in stress. Negative = improvement. |
| `effective` | boolean | `true` if stress stayed the same or decreased |

**Build self-improving agents:**
- `effective: true` → Current approach works. Continue.
- `effective: false` → Stress increased despite the action. Try a different strategy.

This is a closed-loop system: send signals → get action → follow action → check if it worked → adapt. No other API offers this.

## Trigger Memory

Nefesh doesn't just read the current state — it remembers what stresses each user.

When you send `user_message` and `ai_response` alongside biometric signals, Nefesh automatically:
1. Extracts psychological topics from the conversation
2. Correlates topics with stress levels over time
3. Classifies triggers as **active** (currently causing stress) or **resolved** (stress decreased)

Query a user's trigger profile:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_trigger_memory",
    "arguments": { "subject_id": "user-123" }
  }
}
```

Response:
```json
{
  "triggers": {
    "work_deadline": { "status": "active", "avg_stress": 74, "sessions": 5 },
    "relationship": { "status": "resolved", "avg_stress": 31, "sessions": 3 }
  },
  "active": ["work_deadline"],
  "resolved": ["relationship"]
}
```

## API Key Self-Provisioning

AI agents can get their own free API key without manual signup. The developer only clicks one email link.

**Flow:**

1. Agent calls `request_api_key` with the developer's email
2. API sends a verification email
3. Developer clicks the link in the email
4. Agent polls `check_api_key_status` every 10 seconds
5. Once verified, the next poll returns the API key

```
Agent                       API                     Developer
  |                          |                          |
  |-- request_api_key ------>|                          |
  |<-- {request_id, pending} |-- verification email --->|
  |                          |                          |
  |-- check_api_key_status ->|                          |
  |<-- {status: "pending"} --|                          |
  |                          |       clicks link ------>|
  |-- check_api_key_status ->|                          |
  |<-- {status: "ready",   --|                          |
  |     api_key: "nfsh_..."} |                          |
```

Both tools work **without an API key** — they are auth-free so agents without credentials can self-provision.

Response from `request_api_key`:
```json
{
  "request_id": "vlsIfHPoU8NI6977Ogqb3re_csxj8_fz4Fet8IeG5_g",
  "status": "pending",
  "message": "Verification email sent. Call check_api_key_status every 10 seconds.",
  "expires_in": 900
}
```

Response from `check_api_key_status` (after verification):
```json
{
  "status": "ready",
  "api_key": "nfsh_free_6af7435b0dc5f600b7caf3a76c011c90",
  "tier": "free",
  "monthly_limit": 1000,
  "rate_limit_per_minute": 10,
  "message": "API key activated. Add as X-Nefesh-Key header."
}
```

Free tier: 1,000 calls/month, all signal types, 10 req/min. No credit card.

## Supported Signals

**57 fields across 10 categories.** Send any combination per API call.

| Category | Fields | Fused in v1 |
|----------|--------|-------------|
| Cardiovascular | heart_rate, rmssd, sdnn, pnn50, mean_ibi, ibi_count, spo2 | Yes |
| Vocal | tone, speech_rate, pitch_variability | Yes |
| Visual | expression, gaze, posture, engagement | Yes |
| Textual | sentiment (-1.0 to 1.0), urgency | Yes |
| Metabolic | glucose_mg_dl, glucose_mmol_l, glucose_trend | Planned |
| Neural | eeg_alpha_power, eeg_beta_power, eeg_theta_power, cognitive_load | Planned |
| Electrodermal | eda, skin_temperature | Planned |
| Respiratory | respiratory_rate | Planned |
| Movement | steps_last_minute, activity_level | Planned |
| Sleep | sleep_stage | Planned |

> **Note:** `sentiment` is a **float** (-1.0 to 1.0), not a string. The field `sdnn` has no prefix — use `sdnn`, not `hrv_sdnn`.

## Quick test

After adding the config, ask your AI agent:

> "What tools do you have from Nefesh?"

It should list the 7 tools above.

## State labels

| Score | State | `suggested_action` |
|-------|-------|--------------------|
| 0-19 | Calm | `maintain_engagement` |
| 20-39 | Relaxed | `maintain_engagement` |
| 40-59 | Focused | `simplify_and_focus` |
| 60-79 | Stressed | `de-escalate_and_shorten` |
| 80-100 | Acute Stress | `pause_and_ground` |

## Pricing

| Plan | Price | API Calls | Rate Limit |
|------|-------|-----------|------------|
| **Free** | $0 | 1,000/month | 10 req/min |
| **Solo** | $25/month | 50,000/month | 120 req/min |
| **Enterprise** | Custom | Unlimited | Custom SLA |

Get your free key at [nefesh.ai/signup](https://nefesh.ai/signup). No credit card required.

## Authentication

API Key Format: `nfsh_...` — get yours at [nefesh.ai/signup](https://nefesh.ai/signup) or let your agent self-provision one via `request_api_key`.

Pass it via the `X-Nefesh-Key` header in your MCP config (see setup above).

`request_api_key` and `check_api_key_status` are the only tools that work without an API key.

## Documentation

- [Quick Start](https://nefesh.ai/docs/quickstart)
- [API Reference](https://nefesh.ai/llms-full.txt)
- [State Mapping](https://nefesh.ai/docs/states)

## Privacy

- No video uploads — edge processing runs client-side
- No PII stored — strict schema validation
- GDPR/BIPA compliant — cascading deletion via `delete_subject`
- Not a medical device — for contextual AI adaptation only

## License

MIT — see [LICENSE](LICENSE).
