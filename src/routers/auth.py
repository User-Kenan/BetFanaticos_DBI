from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException

# gibt an ,das im HTTP-Header nach einem feld mit diesem Namen gesucht wird
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str=Security(api_key_header)):
    if api_key != "password":
        raise HTTPException(status_code=401,detail="Invalid API Key")
    return api_key