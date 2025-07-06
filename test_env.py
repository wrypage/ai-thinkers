import os
from dotenv import load_dotenv

load_dotenv()  # make sure this runs first

print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
