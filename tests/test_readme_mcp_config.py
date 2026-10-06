"""Checks the MCP setup shown in README.md.

The README shows how to expose two tools through the Apify MCP server:
`fetch-actor-details` and the Actor `conserving_celerytop/live-jobs-http-api`.
These tests make sure every config block in the README lists both, and that the
JSON blocks are valid. No network is used.
"""

import json
import re
from pathlib import Path

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")

MCP_URL = "https://mcp.apify.com/?tools=fetch-actor-details,conserving_celerytop/live-jobs-http-api"
DECLARED_TOOLS = ["fetch-actor-details", "conserving_celerytop/live-jobs-http-api"]


def code_blocks(language):
    return re.findall(rf"```{language}\n(.*?)```", README, flags=re.S)


def test_every_json_block_is_valid_json():
    blocks = code_blocks("json")
    assert blocks, "README has no json blocks"
    for block in blocks:
        json.loads(block)


def test_mcp_url_is_the_documented_one_and_lists_both_tools():
    assert MCP_URL in README
    query = MCP_URL.split("?tools=")[1].split(",")
    assert query[0] == "fetch-actor-details"
    assert "/".join(query[1:]) == "conserving_celerytop/live-jobs-http-api"


def test_each_json_mcp_config_uses_the_url():
    configs = [json.loads(b) for b in code_blocks("json") if "mcp" in b.lower()]
    assert configs, "README has no MCP json config"
    for cfg in configs:
        servers = cfg.get("mcpServers") or cfg.get("servers")
        assert servers, "config has no server list"
        for server in servers.values():
            assert server["url"] == MCP_URL


def test_claude_code_command_names_both_tools():
    commands = [b for b in code_blocks("bash") if "claude mcp add" in b]
    assert commands, "README has no claude mcp add command"
    for command in commands:
        for tool in DECLARED_TOOLS:
            assert tool in command


def test_token_is_never_shown_as_a_real_value():
    assert not re.search(r"apify_api_[A-Za-z0-9]{20,}", README)
