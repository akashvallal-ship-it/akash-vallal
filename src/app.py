import asyncio
from autogen_core import SingleThreadedAgentRuntime
from autogen_agentchat.teams import RoundRobinGroupChat
from agents.coordinator_agent import CoordinatorAgent, CoordinatorInput
from agents.dependency_agent import DependencyAgent
from agents.refactor_agent import RefactorAgent
from agents.testing_agent import TestingAgent
from executors.docker_executor import DockerCommandLineCodeExecutor

async def main():
    runtime = SingleThreadedAgentRuntime()
    # Register all agents
    coordinator = CoordinatorAgent()
    dependency = DependencyAgent()
    refactor = RefactorAgent()
    testing = TestingAgent()
    await CoordinatorAgent.register(runtime, "coordinator", lambda: coordinator)
    await DependencyAgent.register(runtime, "dependency", lambda: dependency)
    await RefactorAgent.register(runtime, "refactor", lambda: refactor)
    await TestingAgent.register(runtime, "testing", lambda: testing)

    # Create a group chat for message-driven workflow
    group = RoundRobinGroupChat(
        [coordinator, dependency, refactor, testing],
        max_round=100,
        speaker_selection_method="auto"
    )

    runtime.start()
    input_data = CoordinatorInput(repo_url="https://github.com/example/repo.git", human_in_the_loop=False)
    await group.run_stream(task=input_data)
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())
