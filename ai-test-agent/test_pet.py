#!/usr/bin/env python3
"""Test script for PET tool verification"""
import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Working directory: {os.getcwd()}")

# Test imports
try:
    import flask
    print(f"Flask version: {flask.__version__}")
except ImportError as e:
    print(f"Flask import error: {e}")

try:
    import openai
    print(f"OpenAI imported successfully")
except ImportError as e:
    print(f"OpenAI import error: {e}")

print("PET test completed successfully!")
