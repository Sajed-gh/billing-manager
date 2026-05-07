import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.environ["GOOGLE_API_KEY"]
MODEL_NAME = os.environ["MODEL_NAME"]