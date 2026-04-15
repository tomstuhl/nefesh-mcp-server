# Nefesh MCP + A2A Server

A [Model Context Protocol](https://modelcontextprotocol.io) and [Agent-to-Agent (A2A)](https://a2a-protocol.org) server that gives AI agents real-time awareness of human physiological state.

## What it does

Send sensor data (heart rate, voice, facial expression, text sentiment), get back a unified state with a machine-readable action your agent can follow directly. Zero prompt engineering required.

On the 2nd+ call, the response includes `adaptation_effectiveness` — telling your agent whether its previous approach actually worked. A closed-loop feedback system for self-improving agents.

## Adaptation Effectiveness (Closed-Loop)

Most APIs give you a state. Nefesh tells you whether your reaction to that state actually worked.

On the 2nd+ call within a session, every response includes:

```json
{
  "state": "focused",
  "stress_score": 45,
  "suggested_action": "simplify_and_focus",
  "adaptation_effectiveness": {
    "previous_action": "de-escalate_and_shorten",
    "previous_score": 68,
    "current_score": 45,
    "stress_delta": -23,
    "effective": true
  }
}
```

Your agent can read `effective: true` and know its previous de-escalation worked. If `effective: false`, the agent adjusts its strategy. No other human-state system provides this feedback loop.

## Setup

### Option A: Connect first, get a key through your agent (fastest)

Add the config **without an API key** — your agent will get one automatically.

```json
{
  "mcpServers": {
    "nefesh": {
      "url": "https://mcp.nefesh.ai/mcp"
    }
  }
}
```

Then ask your agent:

> "Connect to Nefesh and get me a free API key for name@example.com"

The agent calls `request_api_key` → you click one email link → the agent picks up the key. No signup form, no manual copy-paste. After that, add the key to your config for future sessions:

```json
{
  "mcpServers": {
    "nefesh": {
      "url": "https://mcp.nefesh.ai/mcp",
      "headers": {
        "X-Nefesh-Key": "nfsh_free_..."
      }
    }
  }
}
```

### Option B: Get a key first, then connect

Sign up at [nefesh.ai/signup](https://nefesh.ai/signup) (1,000 calls/month, no credit card), then add the config with your key:

```json
{
  "mcpServers": {
    "nefesh": {
      "url": "https://mcp.nefesh.ai/mcp",
      "headers": {
        "X-Nefesh-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Agent-specific config files

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
| **Kiro (Amazon)** | `~/.kiro/mcp.json` |
| **OpenClaw** | `~/.config/openclaw/mcp.json` |
| **JetBrains IDEs** | Settings > Tools > MCP Server |
| **Zed** | `~/.config/zed/settings.json` (uses `context_servers`) |
| **OpenAI Codex CLI** | `~/.codex/config.toml` |
| **Goose CLI** | `~/.config/goose/config.yaml` |
| **ChatGPT Desktop** | Settings > Apps > Add MCP Server (UI) |
| **Gemini CLI** | Settings (UI) |
| **Augment** | Settings Panel (UI) |
| **Replit** | Integrations Page (web UI) |
| **LibreChat** | `librechat.yaml` (self-hosted) |

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

## A2A Integration (Agent-to-Agent Protocol v1.0)

Nefesh is also available as an A2A-compatible agent. While MCP handles tool-calling (your agent calls Nefesh), A2A enables agent-collaboration — other AI agents can communicate with Nefesh as a peer.

**Agent Card:** [`/.well-known/agent-card.json`](https://mcp.nefesh.ai/.well-known/agent-card.json)

**A2A Endpoint:** `POST https://mcp.nefesh.ai/a2a` (JSON-RPC 2.0)

| A2A Skill | Description |
|-----------|-------------|
| `get-human-state` | Stress state (0-100), suggested_action, adaptation_effectiveness |
| `ingest-signals` | Send biometric signals, receive unified state |
| `get-trigger-memory` | Psychological trigger profile (active vs resolved) |
| `get-session-history` | Timestamped history with trend |

Same authentication as MCP — `X-Nefesh-Key` header or `Authorization: Bearer` token. Free tier works on both protocols.

Source: [nefesh-ai/nefesh-a2a](https://github.com/nefesh-ai/nefesh-a2a) · Docs: [nefesh.ai/docs/a2a](https://nefesh.ai/docs/a2a)

## MCP Tools

| Tool | Auth | Description |
|------|:---:|-------------|
| `request_api_key` | No | Request a free API key. You MUST ask the user for their real email first. Do not invent or guess emails. The user receives a verification link they must click. Poll with `check_api_key_status` until ready. |
| `check_api_key_status` | No | Poll for API key activation using the same email the user provided. Returns `pending` or `ready` with API key. |
| `get_human_state` | Yes | Get stress state (0-100), `suggested_action` (maintain/simplify/de-escalate/pause), and `adaptation_effectiveness` — a closed-loop showing whether your previous action reduced stress. |
| `ingest` | Yes | Send biometric signals (heart rate, HRV, voice tone, expression, sentiment, 30+ fields) and get unified state back. Include `subject_id` for trigger memory. |
| `get_trigger_memory` | Yes | Get psychological trigger profile — which topics cause stress (active) and which have been resolved over time. |
| `get_session_history` | Yes | Get timestamped state history with trend (rising/falling/stable). |

## How self-provisioning works

Your AI agent can get a free API key autonomously. You only click one email link.

1. Agent asks you: "What is your email address?"
2. Agent calls `request_api_key(your_real_email)`. No API key needed for this call.
3. You receive a verification email and click the link
4. Agent polls `check_api_key_status(your_real_email)` every 10 seconds
5. Once verified, the agent receives the API key and can use all other tools

**Important:** The agent must use your real, accessible email address. Disposable emails are blocked. The verification link must be clicked by you to activate the key.

Free tier: 1,000 calls/month, all signal types, 10 req/min. No credit card.

## Quick test

After adding the config, ask your AI agent:

> "What tools do you have from Nefesh?"

It should list the 6 tools above.

## Pricing

| Plan | Price | API Calls |
|------|-------|-----------|
| **Free** | $0 | 1,000/month, no credit card |
| **Solo** | $25/month | 50,000/month |
| **Enterprise** | Custom | Custom SLA |

## CLI Alternative

Prefer the terminal over MCP? Use the Nefesh CLI (10-32x lower token cost than MCP for AI agents):

```bash
npm install -g @nefesh/cli
nefesh ingest --session test --heart-rate 72 --tone calm
nefesh state test --json
```

GitHub: [nefesh-ai/nefesh-cli](https://github.com/nefesh-ai/nefesh-cli)

## Gateway Alternative

Want the AI to adapt automatically? Use the [Nefesh Cognitive Compute Router](https://gateway.nefesh.ai). Change your LLM base URL to `gateway.nefesh.ai` and the gateway adjusts system prompt and temperature based on biometric state. Three modes: OpenAI-compatible (`/v1/chat/completions`), Anthropic passthrough (`/v1/messages`), and Unified Anthropic for any backend. Zero code changes.

GitHub: [nefesh-ai/nefesh-gateway](https://github.com/nefesh-ai/nefesh-gateway)

## Human State Protocol (HSP)

Nefesh implements and maintains the [Human State Protocol](https://github.com/nefesh-ai/human-state-protocol), an open specification for exchanging human physiological state between AI systems. HSP defines a standard JSON format for stress scores, behavioral recommendations, and adaptation feedback so any agent can produce or consume human state data interoperably. Apache 2.0.

GitHub: [nefesh-ai/human-state-protocol](https://github.com/nefesh-ai/human-state-protocol) · Docs: [nefesh.ai/docs/hsp](https://nefesh.ai/docs/hsp)

## Documentation

- [Full API Reference](https://nefesh.ai/llms-full.txt)
- [Quick Start](https://nefesh.ai/docs/quickstart)
- [State Mapping](https://nefesh.ai/docs/states)
- [MCP Server](https://nefesh.ai/docs/mcp) · [Source](https://github.com/nefesh-ai/nefesh-mcp-server)
- [A2A Server](https://nefesh.ai/docs/a2a) · [Source](https://github.com/nefesh-ai/nefesh-a2a)
- [Cognitive Compute Router (Gateway)](https://nefesh.ai/docs/gateway) · [Source](https://github.com/nefesh-ai/nefesh-gateway)
- [CLI](https://nefesh.ai/docs/cli) · [Source](https://github.com/nefesh-ai/nefesh-cli)
- [Human State Protocol (HSP)](https://nefesh.ai/docs/hsp) · [Source](https://github.com/nefesh-ai/human-state-protocol)
- [A2A Agent Card](https://mcp.nefesh.ai/.well-known/agent-card.json)
- [A2A Protocol Spec](https://a2a-protocol.org/latest/specification/)

## Privacy

- No video or audio uploads — edge processing runs client-side
- No PII stored
- GDPR/BIPA compliant — cascading deletion via `delete_subject`
- Not a medical device — for contextual AI adaptation only

## License

MIT — see [LICENSE](LICENSE).
