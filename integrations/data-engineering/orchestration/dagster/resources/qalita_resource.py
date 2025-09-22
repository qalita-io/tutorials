import os
import shlex
import io
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict, Optional, Sequence, Union

from dagster import ConfigurableResource

# Use qalita as a Python package (tools-cli). We'll programmatically invoke the Click CLI.
from qalita.__main__ import cli as qalita_cli, add_commands_to_cli


class QalitaResource(ConfigurableResource):
    """Dagster resource wrapping the QALITA CLI (python package invocation).

    Configuration fields can be provided via Dagster resource config or environment variables.
    Environment variable fallbacks:
    - QALITA_AGENT_ENDPOINT
    - QALITA_AGENT_TOKEN
    - QALITA_AGENT_NAME (default: "dagster-agent")
    - QALITA_AGENT_MODE (default: "job")
    """

    endpoint: Optional[str] = None
    token: Optional[str] = None
    agent_name: Optional[str] = "dagster-agent"
    agent_mode: Optional[str] = "job"
    cwd: Optional[str] = None
    log_output: bool = True

    def _build_args(self, command: Union[str, Sequence[str]]) -> Sequence[str]:
        if isinstance(command, str):
            return shlex.split(command)
        return list(command)

    def _gather_env(self, extra_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        env: Dict[str, str] = {}
        # Resolve from config, then environment
        endpoint = self.endpoint or os.environ.get("QALITA_AGENT_ENDPOINT")
        token = self.token or os.environ.get("QALITA_AGENT_TOKEN")
        agent_name = self.agent_name or os.environ.get("QALITA_AGENT_NAME") or "dagster-agent"
        agent_mode = self.agent_mode or os.environ.get("QALITA_AGENT_MODE") or "job"

        if endpoint:
            env["QALITA_AGENT_ENDPOINT"] = endpoint
        if token:
            env["QALITA_AGENT_TOKEN"] = token
        if agent_name:
            env["QALITA_AGENT_NAME"] = agent_name
        if agent_mode:
            env["QALITA_AGENT_MODE"] = agent_mode

        if extra_env:
            env.update(extra_env)
        return env

    def _with_temp_cwd_and_env(self, func, env: Dict[str, str]) -> Any:
        previous_cwd = os.getcwd()
        previous_env: Dict[str, Optional[str]] = {}
        for key, value in env.items():
            previous_env[key] = os.environ.get(key)
        try:
            if self.cwd:
                os.chdir(self.cwd)
            os.environ.update(env)
            return func()
        finally:
            # restore env
            for key, prev in previous_env.items():
                if prev is None and key in os.environ:
                    del os.environ[key]
                elif prev is not None:
                    os.environ[key] = prev
            # restore cwd
            if self.cwd:
                os.chdir(previous_cwd)

    def run(self, command: Union[str, Sequence[str]], env: Optional[Dict[str, str]] = None) -> str:
        """Run a QALITA CLI command via the python package, returning stdout.

        Raises RuntimeError on non-zero exit code or unexpected exceptions.
        """
        args = self._build_args(command)

        # Ensure CLI commands are registered
        add_commands_to_cli()

        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        def _invoke_cli() -> int:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # Use Click's main entry with standalone_mode=False to avoid sys.exit
                return int(
                    qalita_cli.main(
                        args=args,
                        prog_name="qalita",
                        standalone_mode=False,
                    )
                    or 0
                )

        # Merge environment overrides (resource config/env + per-call env)
        env_overrides = self._gather_env(extra_env=env)

        try:
            return_code = self._with_temp_cwd_and_env(_invoke_cli, env_overrides)
        except SystemExit as exc:
            return_code = int(getattr(exc, "code", 1) or 0)
        except Exception as exc:
            err = stderr_buffer.getvalue()
            if self.log_output and err:
                # Best-effort print to stdout; Dagster ops can still capture logs
                print(err.rstrip())
            raise RuntimeError(f"QALITA CLI raised an exception: {exc}")

        out = stdout_buffer.getvalue()
        err = stderr_buffer.getvalue()

        if self.log_output:
            if out:
                print(out.rstrip())
            if err:
                # click may send warnings/info to stderr
                print(err.rstrip())

        if return_code != 0:
            raise RuntimeError(
                f"QALITA CLI exited with code {return_code}. Stderr: {err}"
            )

        return out


