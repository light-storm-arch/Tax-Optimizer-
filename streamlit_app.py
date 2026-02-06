"""Streamlit Cloud entrypoint.

This module imports and executes the app UI from `app.py`.
"""

from app import render_app


if __name__ == "__main__":
    render_app()
