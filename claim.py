from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import random

# 1. Connect to Avalanche Fuji Testnet RPC
AVALANCHE_FUJI_RPC = "https://api.avax-test.network/ext/bc/C/rpc"
w3 = Web3(Web3.HTTPProvider(AVALANCHE_FUJI_RPC))

# Inject PoA middleware (Crucial for Avalanche / EVM sidechains)
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# 2. Set up wallet using private key
PRIVATE_KEY = "a77ab01ad2a7b3129adeafe47ac19b14a1c72cfca8130399225d0fe19d3e2217"
account = w3.eth.account.from_key(PRIVATE_KEY)
my_address = account.address

print(f"Using address: {my_address}")
print(f"Current balance: {w3.eth.get_balance(my_address)} Wei")

# 3. Contract Details provided in assignment
CONTRACT_ADDRESS = "0x85ac2e065d4526FBeE6a2253389669a12318A412"

ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "nonce", "type": "uint256"}],
        "name": "claim",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# 4. Search for a nonce that gives a small token ID
# Note: Solidity's keccak256(abi.encodePacked(nonce)) can be simulated or you can loop 
# and test nonces. Since we want a small tokenId, let's look for a nonce 
# where the hash modulo maxId yields a very small number.
# Alternatively, you can search or test nonces in a loop:

print("Searching for a small token ID nonce...")
found = False

for i in range(1, 10000):
    test_nonce = random.randint(1, 10000000)
    
    # Optional: If you want to check the resulting token ID locally before sending:
    # tokenId = int(w3.keccak(text=str(test_nonce)).hex(), 16) % maxId
    # For a simpler approach, you can just try claiming a few low-range nonces 
    # or loop until a transaction goes through successfully with a low target.
    
    # Let's try a direct approach: testing sequential nonces starting from 1
    nonce = i 
    
    try:
        nonce_count = w3.eth.get_transaction_count(my_address)
        txn = contract.functions.claim(nonce).build_transaction({
            'chainId': 43113,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce_count,
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"Tried nonce {nonce} | Transaction sent: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Success! Claimed with nonce {nonce} in block {receipt.blockNumber}")
        found = True
        break
    except Exception as e:
        # Fails if nonce already used or tokenId taken/reverted
        continue

if not found:
    print("Could not find an open low nonce automatically, try adjusting the loop range.")
