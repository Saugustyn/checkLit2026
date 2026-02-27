import sys
import os

# Dodaje folder backend/ do sys.path, żeby import app.* działał
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))