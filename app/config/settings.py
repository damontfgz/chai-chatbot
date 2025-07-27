import os

# LLM client configuration
MODEL_SERVING_ENDPOINT = os.getenv(
    "MODEL_SERVING_ENDPOINT",
    "http://guanaco-submitter.guanaco-backend.k2.chaiverse.com/endpoints/onsite/chat"
)

API_TOKEN = os.getenv(
    "API_TOKEN",
    "CR_14d43f2bf78b4b0590c2a8b87f354746"
)

# Redis client configuration
REDIS_URL = os.getenv("REDIS_URL", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Postgres client configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")