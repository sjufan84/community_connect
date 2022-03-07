# %%
import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

def convert_df_to_json(dataframe):
    json_data = dataframe.to_json(orient='split')
    data = {"pinataOptions": {"cidVersion": 1}, "pinataContent": json_data}
    return json.dumps(data)

def pin_json_to_ipfs(json):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=json,
        headers=headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def retrieve_block_df(ipfs_hash):
    response = requests.get(f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}').json()
    df = pd.read_json(response, typ='frame', orient='split')

    return df


