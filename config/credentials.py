import os

from dotenv import load_dotenv

load_dotenv()

INVITE_CODE_MANAGER = os.getenv("INVITE_CODE_MANAGER", "")
INVITE_CODE_ADMIN = os.getenv("INVITE_CODE_ADMIN", "")
