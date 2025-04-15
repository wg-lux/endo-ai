#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import dotenv # Import dotenv

def strip_quotes(value):
    """Removes leading/trailing quotes from a string if present."""
    if value:
        return value.strip('"\'')
    return value

def main():
    """Run administrative tasks."""
    # Load .env file explicitly if needed (often handled by direnv/devenv)
    dotenv.load_dotenv()

    # --- Start: Ensure correct DJANGO_SETTINGS_MODULE ---
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
    if settings_module:
        stripped_settings_module = strip_quotes(settings_module)
        if stripped_settings_module != settings_module:
            print(f"manage.py: Stripped quotes from DJANGO_SETTINGS_MODULE ('{settings_module}' -> '{stripped_settings_module}')")
            os.environ['DJANGO_SETTINGS_MODULE'] = stripped_settings_module
        else:
            # Optional: print confirmation even if no stripping occurred
            print(f"manage.py: Using DJANGO_SETTINGS_MODULE='{settings_module}'")
    else:
        # Default fallback if not set (Django's default behavior)
        # Or raise an error if it's required
        print("manage.py: Warning - DJANGO_SETTINGS_MODULE environment variable not set.")
        # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'endo_ai.settings') # Example default
    # --- End: Ensure correct DJANGO_SETTINGS_MODULE ---

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
