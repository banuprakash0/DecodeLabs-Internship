"""
Main CLI entry point and terminal user interface for Enterprise Password Generator.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text

from config import PasswordPolicy, APP_NAME, APP_VERSION
from generator import SecurePasswordGenerator
from validator import validate_length, validate_count, validate_policy
from strength import check_password_strength
from history import GenerationHistory
from utils import sanitize_input

console = Console()
history = GenerationHistory()

DEFAULT_POLICY = PasswordPolicy()


def display_header() -> None:
    """Display the main application header box."""
    header_panel = Panel(
        Text("🔐 ENTERPRISE PASSWORD GENERATOR", style="bold cyan", justify="center"),
        subtitle=f"DecodeLabs Project 3 | v{APP_VERSION}",
        subtitle_align="center",
        border_style="bright_blue",
        expand=False,
    )
    console.print(header_panel)


def display_menu() -> None:
    """Display main CLI menu options."""
    console.print("\n[bold yellow]Main Menu[/bold yellow]")
    console.print("[cyan][1][/cyan] Generate Password")
    console.print("[cyan][2][/cyan] Generate Multiple Passwords")
    console.print("[cyan][3][/cyan] Password Strength Check")
    console.print("[cyan][4][/cyan] Password Policy Settings")
    console.print("[cyan][5][/cyan] Generation History")
    console.print("[cyan][6][/cyan] Security Information")
    console.print("[cyan][0][/cyan] Exit\n")


def handle_generate_single(policy: PasswordPolicy) -> None:
    """Handler for menu item [1]: Generate single password."""
    console.print("\n[bold cyan]─── Generate Password ───[/bold cyan]")

    while True:
        raw_length = Prompt.ask("[bold yellow]Enter password length[/bold yellow]")
        is_valid, length, error_msg = validate_length(raw_length, policy)
        if is_valid:
            break
        console.print(f"[bold red]{error_msg}[/bold red]\n")

    try:
        generator = SecurePasswordGenerator(policy)
        password = generator.generate(length)
        analysis = check_password_strength(password)

        # Record non-sensitive metadata in history
        history.record_generation(length, policy, analysis["rating"])

        # Render generated password display
        console.print("\n[bold green]✓ Password Generated Successfully![/bold green]")
        
        pwd_panel = Panel(
            Text(password, style="bold bright_white on blue", justify="center"),
            title="Secure Password",
            border_style="green",
            expand=False,
        )
        console.print(pwd_panel)

        # Render quick strength breakdown table
        table = Table(title="Password Analysis", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="left")

        table.add_row("Length", str(analysis["length"]))
        table.add_row("Entropy", f"{analysis['entropy_bits']} bits")
        
        rating_color = {
            "VERY WEAK": "red",
            "WEAK": "bright_red",
            "MEDIUM": "yellow",
            "STRONG": "green",
            "VERY STRONG": "bold bright_green",
        }.get(analysis["rating"], "white")

        table.add_row("Strength Rating", f"[{rating_color}]{analysis['rating']}[/{rating_color}]")
        console.print(table)

    except Exception as e:
        console.print(f"[bold red]❌ Error generating password: {e}[/bold red]")


def handle_generate_multiple(policy: PasswordPolicy) -> None:
    """Handler for menu item [2]: Generate multiple passwords."""
    console.print("\n[bold cyan]─── Generate Multiple Passwords ───[/bold cyan]")

    while True:
        raw_count = Prompt.ask("[bold yellow]How many passwords?[/bold yellow]")
        is_valid_c, count, err_c = validate_count(raw_count)
        if is_valid_c:
            break
        console.print(f"[bold red]{err_c}[/bold red]\n")

    while True:
        raw_length = Prompt.ask("[bold yellow]Password length?[/bold yellow]")
        is_valid_l, length, err_l = validate_length(raw_length, policy)
        if is_valid_l:
            break
        console.print(f"[bold red]{err_l}[/bold red]\n")

    try:
        generator = SecurePasswordGenerator(policy)
        passwords = generator.generate_multiple(count, length)

        table = Table(title=f"Generated Passwords ({count} items)", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Password", style="bold white")
        table.add_column("Strength", style="green")

        for idx, pwd in enumerate(passwords, 1):
            analysis = check_password_strength(pwd)
            history.record_generation(length, policy, analysis["rating"])
            table.add_row(str(idx), pwd, analysis["rating"])

        console.print("\n", table)

    except Exception as e:
        console.print(f"[bold red]❌ Error generating multiple passwords: {e}[/bold red]")


def handle_strength_check() -> None:
    """Handler for menu item [3]: Manual Password Strength Check."""
    console.print("\n[bold cyan]─── Password Strength Check ───[/bold cyan]")
    password = Prompt.ask("[bold yellow]Enter password to analyze[/bold yellow]", password=True)
    if not password:
        console.print("[bold red]❌ Password cannot be empty.[/bold red]")
        return

    analysis = check_password_strength(password)

    table = Table(title="Password Strength Analysis", show_header=False)
    table.add_column("Property", style="bold cyan")
    table.add_column("Status / Value", style="white")

    table.add_row("Length", str(analysis["length"]))
    table.add_row("Uppercase", "✓" if analysis["has_uppercase"] else "✗")
    table.add_row("Lowercase", "✓" if analysis["has_lowercase"] else "✗")
    table.add_row("Numbers", "✓" if analysis["has_numbers"] else "✗")
    table.add_row("Special Characters", "✓" if analysis["has_special"] else "✗")
    table.add_row("Character Pool Size", str(analysis["pool_size"]))
    table.add_row("Entropy", f"{analysis['entropy_bits']} bits")

    rating_color = {
        "VERY WEAK": "red",
        "WEAK": "bright_red",
        "MEDIUM": "yellow",
        "STRONG": "green",
        "VERY STRONG": "bold bright_green",
    }.get(analysis["rating"], "white")

    table.add_row("Strength Rating", f"[{rating_color}]{analysis['rating']}[/{rating_color}]")

    console.print("\n", table)

    if analysis["recommendations"]:
        console.print("\n[bold yellow]Recommendations:[/bold yellow]")
        for rec in analysis["recommendations"]:
            console.print(f" • [dim]{rec}[/dim]")


def handle_policy_settings(policy: PasswordPolicy) -> None:
    """Handler for menu item [4]: Configure Password Policy."""
    console.print("\n[bold cyan]─── Password Policy Settings ───[/bold cyan]")

    table = Table(title="Current Policy Configuration", show_header=True, header_style="bold yellow")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Minimum Length", str(policy.min_length))
    table.add_row("Maximum Length", str(policy.max_length))
    table.add_row("Include Uppercase", "✓ Enabled" if policy.include_uppercase else "✗ Disabled")
    table.add_row("Include Lowercase", "✓ Enabled" if policy.include_lowercase else "✗ Disabled")
    table.add_row("Include Numbers", "✓ Enabled" if policy.include_numbers else "✗ Disabled")
    table.add_row("Include Special Characters", "✓ Enabled" if policy.include_special else "✗ Disabled")

    console.print(table)

    if Confirm.ask("\nWould you like to modify policy settings?", default=False):
        policy.include_uppercase = Confirm.ask("Include Uppercase letters (A-Z)?", default=policy.include_uppercase)
        policy.include_lowercase = Confirm.ask("Include Lowercase letters (a-z)?", default=policy.include_lowercase)
        policy.include_numbers = Confirm.ask("Include Numbers (0-9)?", default=policy.include_numbers)
        policy.include_special = Confirm.ask("Include Special Characters (!@#$...)?", default=policy.include_special)

        valid, err = validate_policy(policy)
        if not valid:
            console.print(f"\n[bold red]❌ Invalid policy change: {err}[/bold red]")
            console.print("[yellow]Reverting to default policy.[/yellow]")
            policy.include_uppercase = True
            policy.include_lowercase = True
            policy.include_numbers = True
            policy.include_special = True
        else:
            console.print("\n[bold green]✓ Policy updated successfully![/bold green]")


def handle_history_view() -> None:
    """Handler for menu item [5]: View Generation History."""
    console.print("\n[bold cyan]─── Generation History ───[/bold cyan]")
    records = history.get_records()

    if not records:
        console.print("[dim]No generation history logged in this session.[/dim]")
        return

    table = Table(title=f"Session Generation History ({len(records)} entries)", show_header=True, header_style="bold blue")
    table.add_column("Timestamp", style="dim")
    table.add_column("Length", justify="right")
    table.add_column("Active Classes", style="cyan")
    table.add_column("Strength", style="green")

    for rec in records:
        table.add_row(
            rec["timestamp"],
            str(rec["length"]),
            rec["classes"],
            rec["strength"],
        )

    console.print(table)
    console.print("\n[bold green]🔒 Note: Plaintext passwords are NEVER stored in history records.[/bold green]")

    if Confirm.ask("\nClear session history?", default=False):
        history.clear_history()
        console.print("[bold green]✓ History cleared.[/bold green]")


def handle_security_info() -> None:
    """Handler for menu item [6]: Display Security Information."""
    console.print("\n[bold cyan]─── Security Information & Architecture ───[/bold cyan]")

    info_text = (
        "[bold white]1. Cryptographic Pseudorandom Number Generator (CSPRNG)[/bold white]\n"
        "   This application strictly utilizes Python's [bold green]secrets[/bold green] module "
        "(leveraging OS-level entropy sources like /dev/urandom or CryptGenRandom).\n"
        "   Standard pseudo-random generators like [bold red]random.choice()[/bold red] are insecure "
        "because their internal MT19937 state can be reconstructed after observing output.\n\n"
        "[bold white]2. Character Set Diversity & Policy Guarantees[/bold white]\n"
        "   Character pools are sourced from standard library [bold green]string[/bold green] constants "
        "(ascii_uppercase, ascii_lowercase, digits, punctuation).\n"
        "   The generation algorithm guarantees that at least one character from each selected class "
        "is present in every password.\n\n"
        "[bold white]3. Secure Accumulator Pattern & Shuffling[/bold white]\n"
        "   Passwords are built using a list accumulator and [bold green]''.join()[/bold green] for O(n) "
        "string construction, then shuffled using [bold green]secrets.SystemRandom().shuffle()[/bold green].\n\n"
        "[bold white]4. Zero Plaintext Storage[/bold white]\n"
        "   No generated passwords are saved to disk or persistent storage. Generation history tracks "
        "only non-sensitive metadata (length, classes, timestamp, strength rating)."
    )

    console.print(Panel(info_text, border_style="cyan", title="🔐 Security Specifications"))


def main() -> None:
    """Main CLI interaction loop."""
    current_policy = DEFAULT_POLICY

    while True:
        display_header()
        display_menu()

        choice = Prompt.ask("[bold yellow]Select an option[/bold yellow]", default="0")
        choice = sanitize_input(choice)

        if choice == "1":
            handle_generate_single(current_policy)
        elif choice == "2":
            handle_generate_multiple(current_policy)
        elif choice == "3":
            handle_strength_check()
        elif choice == "4":
            handle_policy_settings(current_policy)
        elif choice == "5":
            handle_history_view()
        elif choice == "6":
            handle_security_info()
        elif choice == "0":
            console.print("\n[bold green]Thank you for using Enterprise Password Generator! Goodbye. 🔐[/bold green]")
            sys.exit(0)
        else:
            console.print("\n[bold red]❌ Invalid option. Please enter a number between 0 and 6.[/bold red]")

        Prompt.ask("\n[dim]Press Enter to return to main menu...[/dim]")


if __name__ == "__main__":
    main()
