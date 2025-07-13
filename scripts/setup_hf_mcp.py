import os
import json
from pathlib import Path

HF_SERVER_NAME = "hf-mcp"
HF_SERVER_CONFIG = {
    "name": HF_SERVER_NAME,
    "description": "HuggingFace MCP tools",
    "url": "https://huggingface.co/mcp",
    # headers will be added dynamically
    "init_timeout": 10,
    "tool_timeout": 200,
}


def load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def save_settings(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4))


def parse_servers(value: str):
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except Exception:
        return []
    if isinstance(parsed, dict):
        # legacy object style
        if "mcpServers" in parsed and isinstance(parsed["mcpServers"], dict):
            return list(parsed["mcpServers"].values())
        else:
            return [parsed]
    if isinstance(parsed, list):
        return parsed
    return []


def main():
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN environment variable not set")

    settings_file = Path("tmp/settings.json")
    settings = load_settings(settings_file)

    servers = parse_servers(settings.get("mcp_servers", ""))

    HF_SERVER_CONFIG["headers"] = {"Authorization": f"Bearer {token}"}

    updated = False
    for i, srv in enumerate(servers):
        if srv.get("name") == HF_SERVER_NAME:
            servers[i] = HF_SERVER_CONFIG
            updated = True
            break
    if not updated:
        servers.append(HF_SERVER_CONFIG)

    settings["mcp_servers"] = json.dumps(servers)
    save_settings(settings_file, settings)
    print(f"Saved HuggingFace MCP server config to {settings_file}")


if __name__ == "__main__":
    main()
