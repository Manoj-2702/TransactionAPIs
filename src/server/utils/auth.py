import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import pandas as pd
from ..database import verify_key, insert_key, get_keys, delete_key


API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
  if not verify_key(api_key):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid API Key")


async def sync_api_keys():
    # print("before keys are got")
    api_keys = pd.read_csv(os.environ["API_KEY_S3_BUCKET"], header=None)
    # print("keys got!")
    db_keys = get_keys()
    api_keys = api_keys[0].values.tolist()
    result = []
    for n in set(api_keys + db_keys):
        result.append((n if n in api_keys else None, n if n in db_keys else None))
    pairs = result
    for tup in pairs:
        if tup[0] == None:
        # must be deleted
            delete_key(tup[1])
        elif tup[1] == None:
        # must be inserted
            insert_key(tup[0])
    print("api_keys synced!")
