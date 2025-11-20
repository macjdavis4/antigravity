#!/usr/bin/env python3
"""Verify setup and dependencies for NFL Fantasy Agent."""
import sys


def check_python_version():
    """Check Python version."""
    print("Checking Python version...", end=" ")
    if sys.version_info >= (3, 8):
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
        return True
    else:
        print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} (need 3.8+)")
        return False


def check_dependencies():
    """Check if all required packages are installed."""
    print("\nChecking dependencies...")

    dependencies = [
        'requests',
        'pandas',
        'numpy',
        'dotenv',
        'schedule',
        'tabulate'
    ]

    all_good = True

    for dep in dependencies:
        try:
            if dep == 'dotenv':
                __import__('dotenv')
            else:
                __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (missing)")
            all_good = False

    return all_good


def check_modules():
    """Check if all custom modules load correctly."""
    print("\nChecking custom modules...")

    modules = [
        ('config', 'config.py'),
        ('src.database', 'src/database.py'),
        ('src.data_fetcher', 'src/data_fetcher.py'),
        ('src.analyzer', 'src/analyzer.py'),
        ('src.team_manager', 'src/team_manager.py'),
        ('src.trade_recommender', 'src/trade_recommender.py')
    ]

    all_good = True

    for module_name, file_name in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {file_name}")
        except Exception as e:
            print(f"  ✗ {file_name} ({str(e)})")
            all_good = False

    return all_good


def main():
    """Run all checks."""
    print("=" * 60)
    print("NFL FANTASY AGENT - SETUP CHECK")
    print("=" * 60)

    checks = [
        check_python_version(),
        check_dependencies(),
        check_modules()
    ]

    print("\n" + "=" * 60)

    if all(checks):
        print("✓ ALL CHECKS PASSED!")
        print("\nYou're ready to go! Run:")
        print("  python3 main.py")
        print("\nFirst time? Select Option 1 to fetch player data.")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nTo fix:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
