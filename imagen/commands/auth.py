"""Auth subcommand for storing provider credentials."""

from __future__ import annotations

from sys import stderr

from imagen.auth_store import OPENROUTER_PROVIDER, get_keys_file, save_api_key

def run_auth() -> int:
    print("Select provider:")
    print("1. OpenRouter.ai")

    provider_choice = input("Provider [1]: ").strip() or "1"
    if provider_choice != "1":
        print("Unsupported provider selection.", file=stderr)
        return 1

    api_key = input("OpenRouter.ai API key: ").strip()
    if not api_key:
        print("API key must not be empty.", file=stderr)
        return 1

    save_api_key(OPENROUTER_PROVIDER, api_key)
    print(f"Saved OpenRouter.ai API key to {get_keys_file()}")
    return 0
