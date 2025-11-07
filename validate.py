#!/usr/bin/env python
"""Validation script for Space Explorer A2A Agent.

This script validates the agent configuration and setup.
Run this after completing setup to verify everything is configured correctly.
"""

import json
import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def check_files():
    """Check that all required files exist."""
    print_header("Checking Files")

    required_files = [
        "space_agent_a2a/agent.py",
        "space_agent_a2a/agent.json",
        "space_agent_a2a/__init__.py",
        "space_agent_a2a/oauth_helper.py",
        "space_agent_a2a/storage_tool.py",
        "pyproject.toml",
        "requirements.txt",
        "main.py",
        "README.md",
        "SETUP.md",
        "QUICKSTART.md",
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING!")
            all_exist = False

    return all_exist


def check_agent_card():
    """Validate agent.json format."""
    print_header("Validating Agent Card")

    try:
        with open("space_agent_a2a/agent.json", "r") as f:
            agent_card = json.load(f)

        required_fields = ["name", "description", "skills", "url", "version"]
        all_valid = True

        for field in required_fields:
            if field in agent_card:
                print(f"✓ {field}: {agent_card[field] if field != 'skills' else f'{len(agent_card[field])} skills'}")
            else:
                print(f"✗ {field} - MISSING!")
                all_valid = False

        if agent_card.get("url") == "http://localhost:8000/a2a/space_explorer":
            print("\n⚠ Note: URL is set to localhost - update for production deployment")

        return all_valid
    except Exception as e:
        print(f"✗ Failed to load agent.json: {e}")
        return False


def check_env():
    """Check .env configuration."""
    print_header("Checking Environment Configuration")

    env_file = Path("space_agent_a2a/.env")
    env_example = Path("space_agent_a2a/.env.example")

    if not env_example.exists():
        print("✗ .env.example not found!")
        return False
    else:
        print("✓ .env.example exists")

    if not env_file.exists():
        print("✗ .env file not found!")
        print("  → Copy .env.example to .env and configure it")
        return False
    else:
        print("✓ .env file exists")

    # Load .env
    from dotenv import load_dotenv
    load_dotenv("space_agent_a2a/.env")

    required_vars = [
        ("AUTH0_DOMAIN", "Auth0 tenant domain"),
        ("AUTH0_CLIENT_ID", "Auth0 client ID"),
        ("AUTH0_CLIENT_SECRET", "Auth0 client secret"),
        ("AUTH0_API_AUDIENCE", "MCP server URL"),
    ]

    optional_vars = [
        ("GOOGLE_API_KEY", "Gemini API key (recommended)"),
        ("GOOGLE_CLOUD_PROJECT", "GCP project ID"),
        ("ADK_CALLBACK_URL", "OAuth callback URL"),
    ]

    all_required = True
    print("\nRequired variables:")
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if value and value != f"your_{var_name.lower()}_here" and "example" not in value.lower():
            print(f"✓ {var_name} ({description})")
        else:
            print(f"✗ {var_name} ({description}) - NOT CONFIGURED!")
            all_required = False

    print("\nOptional variables:")
    for var_name, description in optional_vars:
        value = os.getenv(var_name)
        if value and value != f"your_{var_name.lower()}_here" and "example" not in value.lower():
            print(f"✓ {var_name} ({description})")
        else:
            print(f"  {var_name} ({description}) - not set")

    # Check that at least one Google auth method is configured
    has_api_key = os.getenv("GOOGLE_API_KEY") and "example" not in os.getenv("GOOGLE_API_KEY", "").lower()
    has_gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT") and "example" not in os.getenv("GOOGLE_CLOUD_PROJECT", "").lower()

    if not (has_api_key or has_gcp_project):
        print("\n⚠ Warning: No Google authentication configured!")
        print("  → Set either GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT")
        all_required = False

    return all_required


def check_imports():
    """Test that agent can be imported."""
    print_header("Testing Agent Imports")

    try:
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from space_agent_a2a import root_agent

            if w:
                for warning in w:
                    if "Auth0" in str(warning.message):
                        print(f"⚠ {warning.message}")

        print(f"✓ Agent imported successfully")
        print(f"  Name: {root_agent.name}")
        print(f"  Model: {root_agent.model}")
        print(f"  Tools: {len(root_agent.tools)} configured")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dependencies():
    """Check that required packages are installed."""
    print_header("Checking Dependencies")

    required_packages = [
        ("google.adk", "google-adk"),
        ("google.auth", "google-auth"),
        ("dotenv", "python-dotenv"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
    ]

    all_installed = True
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - NOT INSTALLED!")
            all_installed = False

    # Check for a2a-sdk (optional for Python 3.10+)
    try:
        import sys
        if sys.version_info >= (3, 10):
            import a2a
            print(f"✓ a2a-sdk (for A2A support)")
        else:
            print(f"  a2a-sdk - skipped (requires Python 3.10+)")
    except ImportError:
        print(f"⚠ a2a-sdk - not installed (needed for A2A features)")

    return all_installed


def main():
    """Run all validation checks."""
    print("""
╔════════════════════════════════════════════════════════════╗
║         Space Explorer A2A Agent - Validation              ║
╚════════════════════════════════════════════════════════════╝
""")

    checks = [
        ("Files", check_files()),
        ("Agent Card", check_agent_card()),
        ("Dependencies", check_dependencies()),
        ("Environment", check_env()),
        ("Imports", check_imports()),
    ]

    print_header("Validation Summary")

    all_passed = True
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("\n🎉 All checks passed! Your agent is ready to run.\n")
        print("Next steps:")
        print("  1. Run standalone: adk web space_agent_a2a")
        print("  2. Run as A2A server: adk api_server --a2a --port 8001 space_agent_a2a")
        print("  3. Test with orchestrator: adk web examples/")
        print("\nSee QUICKSTART.md for more details.\n")
        return 0
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        print("\nSee SETUP.md for detailed configuration instructions.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
