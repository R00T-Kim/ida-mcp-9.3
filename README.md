# IDA MCP for IDA 9.3

An unofficial IDA 9.3 compatibility port of [HexRaysSA/ida-mcp](https://github.com/HexRaysSA/ida-mcp),
based on [d9e415d](https://github.com/HexRaysSA/ida-mcp/tree/d9e415dc88654cbb392802e5c55b3236c090155d).
Original copyright and MIT license are retained.
Compatibility changes are supplied as a patch to [ida-nexus](https://github.com/HexRaysSA/ida-nexus) 0.13.0.

## Install the IDA 9.3 port

This branch supplies an `ida-nexus 0.13.0` compatibility patch. With Git, uv,
and IDA installed, run from this checkout (use your own IDA path):

```bash
uv run --no-project --python 3.14 compat/install.py --idadir /path/to/ida-pro-9.3
```

On Windows, use `--idadir "C:\Program Files\IDA Professional 9.3"`.
Use a Python version matching IDA's configured Python for GUI use. If needed,
add `--license-file /path/to/ida.reg` to copy your license into the isolated profile.
The installer verifies the official source against `uv.lock`, applies the patch,
and installs it into `.ida93/venv`; existing IDA and MCP settings are preserved.

Add the generated `.ida93/mcp.json` entry to your MCP client's configuration.
For GUI use, run `.ida93/venv/bin/python .ida93/run.py --gui /path/to/database-copy`
(on Windows use `.ida93\venv\Scripts\python.exe`). This launches IDA with the
matching plugin and isolated settings. Start with database copies.

Linux and Windows IDA 9.3 integration tests passed. Long native operations can
respond late to cancellation or timeouts; IDA 9.4+ runtime comparison is unverified.
The isolated installer and its MCP/GUI launchers were also tested on both platforms.
Close this build’s MCP and IDA processes before rerunning the installer to update.
Use the generated launcher, not `uvx ida-mcp`,
which installs the official release. To uninstall, remove the client entry,
close these test processes, and delete `.ida93/` (retain any files you need).
Do not run `uv sync` against `.ida93/venv`, as it restores the unpatched dependency.

## Upstream installation (official release)

The instructions below install the official release, not this 9.3 port.

### Requirements

- Installed in your PATH
  - [Git](https://git-scm.com/)
  - [uv](https://github.com/astral-sh/uv)
- IDA 9.4 or higher with idalib and Python 3.11+
- We recommend disabling other IDA MCP servers to reduce agent confusion

### Automatic installation

Install the Hex-Rays IDA MCP using [hcli](https://hcli.docs.hex-rays.com/):

```bash
uvx ida-hcli mcp install
# or if you have hcli installed:
hcli mcp install
```

This will install the GUI plugin and interactively offer you to install the supported agent plugins.

### Manual installation

<details>

<summary>Manual installation instructions...</summary>

#### IDA GUI Plugin

To support IDA GUI instances when using IDA MCP, install the plugin:

```bash
uvx ida-hcli plugin install https://github.com/HexRaysSA/ida-mcp
# or if you have hcli installed:
hcli plugin install https://github.com/HexRaysSA/ida-mcp
```

_Note_: Without the GUI plugin, IDA MCP will still work headlessly.

#### [Claude Code](https://claude.com/product/claude-code)

```bash
# Add Hex-Rays marketplace
claude plugin marketplace add HexRaysSA/claude-marketplace
# Install plugin
claude plugin install ida-mcp@HexRaysSA
# Update to latest version
claude plugin update ida-mcp@HexRaysSA
```

#### [Codex CLI](https://learn.chatgpt.com/docs/codex/cli)

```bash
# Add Hex-Rays marketplace
codex plugin marketplace add HexRaysSA/codex-marketplace
# Install plugin
codex plugin add ida-mcp@HexRaysSA
```

#### [GitHub Copilot CLI](https://github.com/features/copilot/cli)

```bash
# Add Hex-Rays marketplace
copilot plugin marketplace add HexRaysSA/copilot-marketplace
# Install plugin
copilot plugin install ida-mcp@HexRaysSA
# Update to latest version
copilot plugin update ida-mcp
```

#### [Pi](https://pi.dev/)

```bash
# Install extension
pi install git:github.com/HexRaysSA/ida-mcp@latest
# Update to latest version
pi update --extensions
```

#### [oh-my-pi](https://github.com/can1357/oh-my-pi)

```bash
# Install extension
omp plugin install github:HexRaysSA/ida-mcp#latest
# Update to latest version
omp plugin upgrade
```

#### Other agents

Configure a regular stdio MCP server in your MCP JSON configuration:

```json
{
  "mcpServers": {
    "ida": {
      "command": "uvx",
      "args": [
        "--exclude-newer=1s",
        "ida-mcp",
        "stdio",
        "--agent=my-agent"
      ]
    }
  }
}
```

`uvx` resolves the latest stable `ida-mcp` release from PyPI, so this
configuration does not need to be updated for each release.

`--agent=my-agent` is a human-chosen label (like `claude-code`, `cursor`,
`my-custom-agent`, etc.) used to differentiate sessions in the dashboard.

</details>

## CLI

```bash
# MCP server over standard input/output
uvx ida-mcp stdio --agent=my-agent

# MCP server over Streamable HTTP
uvx ida-mcp http --host 127.0.0.1 --port 8737

# Inspect session log
uvx ida-mcp dashboard --open

# Export session logs for troubleshooting
uvx ida-mcp logs
```

## Usage

Start your agent harness and ask it something like:

> Reverse /path/to/sample.elf for me in IDA

To test the GUI integration, open something in IDA and ask your harness:

> What do I have open in the IDA GUI?

## Developers: IDA Nexus

The IDA MCP project is built on [IDA Nexus](https://github.com/HexRaysSA/ida-nexus),
which allows multiple clients to seamlessly share and operate on IDA databases.

You can build your own tools on top of the `ida-nexus` library, see
[the documentation](https://github.com/HexRaysSA/ida-nexus/blob/main/README.md#python-package-developers)
for more information.
