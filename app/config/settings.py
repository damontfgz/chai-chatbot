import os

MODEL_SERVING_ENDPOINT = os.getenv(
    "MODEL_SERVING_ENDPOINT",
    "http://guanaco-submitter.guanaco-backend.k2.chaiverse.com/endpoints/onsite/chat"
)

API_TOKEN = os.getenv(
    "API_TOKEN",
    "CR_14d43f2bf78b4b0590c2a8b87f354746"
)