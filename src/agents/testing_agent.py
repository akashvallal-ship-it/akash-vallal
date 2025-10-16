
# Full pytest-in-Docker agent for Python projects
import os
import shutil
import stat
import re
import time
from pathlib import Path
from pydantic import BaseModel
from autogen_core import RoutedAgent, CancellationToken
from utils.github_utils import clone_repo
from config import Config
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_core.code_executor import CodeBlock

BASE_REPO_DIR = Path("D:/Akash/src/agents/cloned_repos").resolve()

if not BASE_REPO_DIR.exists():
    BASE_REPO_DIR.mkdir(parents=True)

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def remove_tree_with_retries(path: str, retries: int = 5, delay: float = 0.5) -> None:
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            if os.path.exists(path):
                shutil.rmtree(path, onerror=remove_readonly)
            return
        except Exception as e:
            last_exc = e
            if attempt == retries:
                raise
            time.sleep(delay)

class TestResult(BaseModel):
    passed: bool
    report: str
    coverage: float | None = None
    repo_path: str

class TestingAgent(RoutedAgent):
    def __init__(self):
        super().__init__("TestingAgent")

    async def build_and_run_tests(self, repo_url: str):
        print("Cloning repository...")

        repo_dir_name = repo_url.rstrip('/').split('/')[-1]
        host_repo_path = BASE_REPO_DIR / repo_dir_name
        if host_repo_path.exists():
            try:
                remove_tree_with_retries(str(host_repo_path))
            except Exception as e:
                print(f"Warning: Failed to remove existing repo path {host_repo_path}: {e}")
        host_repo_path_str = str(host_repo_path)
        clone_repo(repo_url, clonedir=host_repo_path_str)

        print(f"Repo cloned to host path: {host_repo_path_str}")

        test_result = TestResult(
            passed=False,
            report="Execution did not complete.",
            coverage=None,
            repo_path=host_repo_path_str,
        )
        cancellation_token = CancellationToken()
        try:
            requirements_path = Path(host_repo_path_str) / "requirements.txt"
            install_cmd = ""
            if requirements_path.exists():
                install_cmd = "pip install -r requirements.txt && "
            else:
                print("No requirements.txt found, skipping dependency install.")

            test_cmd = f"{install_cmd}pytest --maxfail=1 --disable-warnings --cov=. > result.log; cat result.log"
            code_blocks = [CodeBlock(language="bash", code=test_cmd)]

            async with DockerCommandLineCodeExecutor(
                work_dir=host_repo_path_str,
                bind_dir=host_repo_path_str,
                image="python:3.10-slim",
                timeout=300,
            ) as executor:
                print("Installing dependencies and running pytest inside Docker...")
                result = await executor.execute_code_blocks(
                    code_blocks, cancellation_token=cancellation_token
                )
                output = result.output
                test_result.report = output

                # Parse for coverage (if pytest-cov is used)
                coverage_match = re.search(r"TOTAL.*?(\d+)%", output)
                if coverage_match:
                    test_result.coverage = float(coverage_match.group(1))
                test_result.passed = "failed" not in output.lower()
                print("Pytest finished.")
                print(f"Coverage: {test_result.coverage or 'N/A'}")
                return test_result
        except Exception as e:
            test_result.report = f"Unexpected error during Docker execution: {e}"
            print(test_result.report)
            return test_result
        finally:
            try:
                remove_tree_with_retries(host_repo_path_str)
                print(f"Cleaned up temporary directory: {host_repo_path_str}")
            except Exception as e:
                print(f"Warning: Failed to cleanup temporary directory {host_repo_path_str}: {e}")

if __name__ == "__main__":
    import asyncio
    async def main():
        print("Starting TestingAgent (Standalone Mode)...")
        agent = TestingAgent()
        repo_url = "https://github.com/akashvallal-ship-it/akash-vallal"
        result = await agent.build_and_run_tests(repo_url)

        print("\n================= FINAL TEST RESULT =================")
        print("Passed!" if result.passed else "❌ Failed!")
        print("Coverage:", result.coverage)
        print("Repo Path:", result.repo_path)
        print("====================================================")
        print("Report snippet (max 1000 chars):\n", result.report[:1000])


    asyncio.run(main())
