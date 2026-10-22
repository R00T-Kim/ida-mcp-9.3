# IDA MCP for IDA 9.3

An unofficial IDA 9.3 compatibility port of [HexRaysSA/ida-mcp](https://github.com/HexRaysSA/ida-mcp),
based on [df6de79](https://github.com/HexRaysSA/ida-mcp/tree/df6de7985b534a964c125d5a86e41b26b17b14f6) (release 20261008.0.1).
Original copyright and MIT license are retained.
Compatibility changes are supplied as a patch to [ida-nexus](https://github.com/HexRaysSA/ida-nexus) 0.13.4.

## Install the IDA 9.3 port

Requires [Git](https://git-scm.com/), [uv](https://docs.astral.sh/uv/),
and a licensed IDA 9.3 installation with idalib. Use your own IDA path:

```bash
git clone https://github.com/R00T-Kim/ida-mcp-9.3.git
cd ida-mcp-9.3
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

On Linux, the 0.13.4-based port passed IDA 9.3 integration tests; Windows was
last verified with the 0.13.0-based port. Long native operations can respond late
to cancellation or timeouts; IDA 9.4+ runtime comparison is unverified.
Three upstream autoanalysis interruption tests assume functions exist 0.25 s
into analysis; IDA 9.3 creates its first function after 1–4 s here, so they can fail.
The isolated installer and its MCP/GUI launchers were also tested on both platforms.
Close this build’s MCP and IDA processes before rerunning the installer to update.
Use the generated launcher, not `uvx ida-mcp`,
which installs the official release. To uninstall, remove the client entry,
close these test processes, and delete `.ida93/` (retain any files you need).
Do not run `uv sync` against `.ida93/venv`, as it restores the unpatched dependency.

## CLI

Use the installed launcher for the server and its utilities:

```bash
.ida93/venv/bin/python .ida93/run.py stdio --agent=my-agent
.ida93/venv/bin/python .ida93/run.py http --host 127.0.0.1 --port 8737
.ida93/venv/bin/python .ida93/run.py dashboard --open
.ida93/venv/bin/python .ida93/run.py logs
```

On Windows, replace `.ida93/venv/bin/python` with `.ida93\venv\Scripts\python.exe`.
For upstream documentation, see [HexRaysSA/ida-mcp](https://github.com/HexRaysSA/ida-mcp).
