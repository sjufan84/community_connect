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

def updateIPFS_df(contract, newBlock_df, sender):
    ipfsHash = contract.functions.getIPFSHash().call()
    if ipfsHash != '':
        ipfs_df = retrieve_block_df(ipfsHash)
        ipfs_df['Contract Balance'] = ipfs_df['Contract Balance'].astype('str')
        new_df = pd.concat([newBlock_df,ipfs_df])
        new_df = new_df[~new_df.index.duplicated(keep='first')]
        new_json_df = convert_df_to_json(new_df)
        newHash = pin_json_to_ipfs(new_json_df)
        tx_hash2 = contract.functions.updateIPFSHash(newHash).transact({
            'from': sender,
        })
    else:
        new_json_df = convert_df_to_json(newBlock_df)
        newHash = pin_json_to_ipfs(new_json_df)
        new_df = newBlock_df
        tx_hash2 = contract.functions.updateIPFSHash(newHash).transact({
            'from': sender,
        })

    return new_df


