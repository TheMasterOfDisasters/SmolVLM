# config.py
"""
Global configuration for model selection and shared settings.
Change MODEL_ID to any of the MODELS list below, then restart the app.
"""
MODELS = [
    "HuggingFaceTB/SmolVLM2-256M-Video-Instruct",
    "HuggingFaceTB/SmolVLM2-500M-Video-Instruct",
    "HuggingFaceTB/SmolVLM2-2.2B-Base",
    "HuggingFaceTB/SmolVLM2-2.2B-Instruct",
]

# Default model (500M Instruct)
MODEL_ID = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"

# Server settings
PORT = 8888
DEMO_IMAGE = "./images/cat.jpg"
