from typing import List, Optional
from rich.prompt import Prompt, InvalidResponse
from rich.console import Console
import typer
import inquirer

console = Console()

class ChoiceValidator:
    def __init__(self, choices: List[str]):
        self.choices = choices

    def __call__(self, response: str) -> str:
        if response not in self.choices:
            raise InvalidResponse(f"Please select one of {self.choices}")
        return response

def prompt_for_choice(prompt_text: str, choices: List[str], default: Optional[str] = None) -> str:
    """Prompts the user to select from a list of choices using arrow key navigation."""
    if not choices:
        console.print("[bold red]No choices available.[/]")
        raise typer.Abort()

    try:
        # Use inquirer for arrow key navigation
        questions = [
            inquirer.List(
                'choice',
                message=prompt_text,
                choices=choices,
                default=default if default and default in choices else choices[0]
            )
        ]
        
        answers = inquirer.prompt(questions)
        if answers is None:
            # User pressed Ctrl+C
            raise KeyboardInterrupt()
            
        return answers['choice']
        
    except (KeyboardInterrupt, EOFError):
        # Fallback to numbered selection if inquirer fails or user cancels
        console.print(f"\n[yellow]Falling back to numbered selection...[/]")
        console.print(prompt_text)
        for i, choice in enumerate(choices, 1):
            console.print(f"  [cyan]{i}[/]. {choice}")
        
        choice_map = {str(i): choice for i, choice in enumerate(choices, 1)}
        
        response = Prompt.ask(
            "Enter the number of your choice", 
            choices=list(choice_map.keys()),
            default="1" if not default else default
        )
        return choice_map[response]

def prompt_for_text(prompt_text: str, default: Optional[str] = None) -> str:
    """Prompts the user for free-form text input."""
    try:
        # Use inquirer for text input to maintain consistency
        questions = [
            inquirer.Text(
                'text',
                message=prompt_text,
                default=default or ""
            )
        ]
        
        answers = inquirer.prompt(questions)
        if answers is None:
            raise KeyboardInterrupt()
            
        return answers['text']
        
    except (KeyboardInterrupt, EOFError):
        # Fallback to rich prompt
        return Prompt.ask(prompt_text, default=default)

def prompt_for_confirmation(prompt_text: str, default: bool = True) -> bool:
    """Prompts the user for yes/no confirmation with arrow key navigation."""
    try:
        questions = [
            inquirer.Confirm(
                'confirm',
                message=prompt_text,
                default=default
            )
        ]
        
        answers = inquirer.prompt(questions)
        if answers is None:
            raise KeyboardInterrupt()
            
        return answers['confirm']
        
    except (KeyboardInterrupt, EOFError):
        # Fallback to rich prompt
        return Prompt.ask(f"{prompt_text} (y/n)", 
                         choices=["y", "n"], 
                         default="y" if default else "n") == "y"
