"""Install the IDA 9.3 compatibility patch into a repository-local environment."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import urllib.request
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--idadir", required=True, type=Path, help="IDA installation directory"
    )
    parser.add_argument(
        "--license-file",
        type=Path,
        help="Optional ida.reg to copy into the isolated IDA user directory",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    idadir = args.idadir.expanduser().resolve()
    gui = idadir / ("ida.exe" if os.name == "nt" else "ida")
    if not gui.is_file():
        parser.error(f"IDA executable not found: {gui}")
    for command in ("uv", "git"):
        if not shutil.which(command):
            parser.error(f"{command} must be installed and available in PATH")
    if args.license_file and not args.license_file.is_file():
        parser.error(f"License file not found: {args.license_file}")
    state = root / ".ida93"
    state.mkdir(exist_ok=True)
    env = dict(os.environ, UV_PROJECT_ENVIRONMENT=str(state / "venv"))
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    python = (
        state / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    package = next(
        p
        for p in tomllib.loads((root / "uv.lock").read_text())["package"]
        if p["name"] == "ida-nexus"
    )
    if package["version"] != "0.13.0":
        raise RuntimeError("This patch requires ida-nexus 0.13.0 in uv.lock")
    with tempfile.TemporaryDirectory(prefix="ida93-source-") as temporary:
        archive = Path(temporary) / "nexus.tar.gz"
        with urllib.request.urlopen(package["sdist"]["url"], timeout=60) as response:
            archive.write_bytes(response.read())
        expected = package["sdist"]["hash"]
        if "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise RuntimeError("Nexus source checksum does not match uv.lock")
        with tarfile.open(archive) as tar:
            tar.extractall(temporary, filter="data")
        source = Path(temporary) / "ida_nexus-0.13.0"
        subprocess.run(
            ["git", "apply", "--check", str(root / "compat/ida-nexus-0.13.0.patch")],
            cwd=source,
            check=True,
        )
        subprocess.run(
            ["git", "apply", str(root / "compat/ida-nexus-0.13.0.patch")],
            cwd=source,
            check=True,
        )
        subprocess.run(
            ["uv", "sync", "--frozen", "--no-dev", "--python", sys.executable],
            cwd=root,
            env=env,
            check=True,
        )
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python),
                "--no-deps",
                "--reinstall-package",
                "ida-nexus",
                str(source),
            ],
            env=env,
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-c",
                "from ida_nexus._runtime import LegacyIdalibDispatcher",
            ],
            cwd=state,
            env=env,
            check=True,
        )
    userdir = state / "idausr"
    plugins = userdir / "plugins" / "ida-mcp"
    plugins.mkdir(parents=True, exist_ok=True)
    if args.license_file:
        destination = userdir / "ida.reg"
        if not destination.exists():
            shutil.copy2(args.license_file, destination)
    site = subprocess.check_output(
        [str(python), "-c", 'import sysconfig; print(sysconfig.get_path("purelib"))'],
        env=env,
        text=True,
    ).strip()
    (plugins / "ida_mcp_plugin.py").write_text(
        "import sys\nsys.path.insert(0, "
        + repr(site)
        + ")\n"
        + (root / "ida_mcp_plugin.py").read_text(),
        encoding="utf-8",
    )
    metadata = json.loads((root / "ida-plugin.json").read_text())
    metadata["plugin"]["idaVersions"] = ">=9.3"
    (plugins / "ida-plugin.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    settings = {
        "IDADIR": str(idadir),
        "IDAUSR": str(userdir),
        "IDA_NEXUS_STATE_DIR": str(state / "nexus-state"),
        "IDA_MCP_STATE_DIR": str(state / "mcp-state"),
    }
    if os.name != "nt":
        (state / "tmp").mkdir(exist_ok=True)
        settings["TMPDIR"] = str(state / "tmp")
    launcher = state / "run.py"
    launcher.write_text(
        "import os, subprocess, sys\n"
        f"os.environ.update({settings!r})\n"
        'os.environ.pop("PYTHONPATH", None)\n'
        'os.environ.pop("PYTHONHOME", None)\n'
        "args = sys.argv[1:]\n"
        f'command = [{str(gui)!r}] + args[1:] if args[:1] == ["--gui"] else [sys.executable, "-c", "from ida_mcp.cli import main; raise SystemExit(main())"] + (args or ["stdio", "--agent=ida93"])\n'
        "raise SystemExit(subprocess.call(command))\n",
        encoding="utf-8",
    )
    config = {
        "mcpServers": {
            "ida93": {
                "command": str(python),
                "args": [str(launcher), "stdio", "--agent=ida93"],
            }
        }
    }
    (state / "mcp.json").write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Installed patched Nexus into {python.parent.parent}")
    print(f"MCP client configuration: {state / 'mcp.json'}")
    print(f'GUI: "{python}" "{launcher}" --gui <database-copy>')


if __name__ == "__main__":
    main()
