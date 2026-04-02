# Nefesh MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that gives AI agents real-time awareness of human physiological state.

## What it does

Send sensor data (heart rate, voice, facial expression, text sentiment), get back a unified state with a machine-readable action your agent can follow directly. Zero prompt engineering required.

On the 2nd+ call, the response includes `adaptation_effectiveness` — telling your agent whether its previous approach actually worked. A closed-loop feedback system for self-improving agents.

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
| **Amazon Q** | `~/.aws/amazonq/mcp.json` |
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

## Tools

| Tool | Auth | Description |
|------|:---:|-------------|
| `request_api_key` | No | Request a free API key by email. Poll with `check_api_key_status` until ready. |
| `check_api_key_status` | No | Poll for API key activation. Returns `pending` or `ready` with API key. |
| `get_human_state` | Yes | Get stress state (0-100), `suggested_action` (maintain/simplify/de-escalate/pause), and `adaptation_effectiveness` — a closed-loop showing whether your previous action reduced stress. |
| `ingest` | Yes | Send biometric signals (heart rate, HRV, voice tone, expression, sentiment, 30+ fields) and get unified state back. Include `subject_id` for trigger memory. |
| `get_trigger_memory` | Yes | Get psychological trigger profile — which topics cause stress (active) and which have been resolved over time. |
| `get_session_history` | Yes | Get timestamped state history with trend (rising/falling/stable). |
| `delete_subject` | Yes | GDPR-compliant cascading deletion of all data for a subject. |

## How self-provisioning works

Your AI agent can get a free API key autonomously. You only click one email link.

1. Agent calls `request_api_key(email)` — no API key needed for this call
2. You receive a verification email and click the link
3. Agent polls `check_api_key_status(request_id)` every 10 seconds
4. Once verified, the agent receives the API key and can use all other tools

Free tier: 1,000 calls/month, all signal types, 10 req/min. No credit card.

## Quick test

After adding the config, ask your AI agent:

> "What tools do you have from Nefesh?"

It should list the 7 tools above.

## Pricing

| Plan | Price | API Calls |
|------|-------|-----------|
| **Free** | $0 | 1,000/month, no credit card |
| **Solo** | $25/month | 50,000/month |
| **Enterprise** | Custom | Custom SLA |

## Documentation

- [Full API Reference](https://nefesh.ai/llms-full.txt)
- [Quick Start](https://nefesh.ai/docs/quickstart)
- [State Mapping](https://nefesh.ai/docs/states)

## Privacy

- No video or audio uploads — edge processing runs client-side
- No PII stored
- GDPR/BIPA compliant — cascading deletion via `delete_subject`
- Not a medical device — for contextual AI adaptation only

## License

MIT — see [LICENSE](LICENSE).
