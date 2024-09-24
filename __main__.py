from dotenv import load_dotenv

load_dotenv() 

from gptLang import GPT, Parameter, GPT_function
import subprocess
import sys

agent = GPT(context="""
You are in control of a kubernetes cluster via kubeapi. The user is a non-devops guy. 
He does not want to know or execute commands at all. Please do everything on your own. Execution and investigation.
Please use tools to answer the question or perform the task.
            """,
            parallel_tool_calls=False,
            print_function_calls=False,) 


def run_kube_command(
    command: str, verbose: bool = False, safe_mode: bool = True
) -> str:
    if not command.startswith("kubectl "): 
        command = f"kubectl {command}"
    
    if safe_mode:
        inp = input(f"[GPT wants to execute] {command}")
        if inp != "":
            return "Script execution was declined by the user"

    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if verbose:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)

    return result.stdout if result.returncode == 0 else result.stderr


def safe_shell_command(command: str) -> str:
    return run_kube_command(command=command, verbose=False, safe_mode=True)


agent.add_function(
    GPT_function(
        name="kubectl", 
        do=safe_shell_command,
        description="Run a kubectl command. Only provide the command without 'kubectl' at the beginning. Examlpe: 'get pods'",
        parameters=[Parameter(name="command", required=True, type=str)],
    )
)


if __name__ == "__main__":
    agent.chat()
