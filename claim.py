from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import random

# 1. Connect to Avalanche Fuji Testnet RPC
AVALANCHE_FUJI_RPC = "https://api.avax-test.network/ext/bc/C/rpc"
w3 = Web3(Web3.HTTPProvider(AVALANCHE_FUJI_RPC))

# Inject PoA middleware (Crucial for Avalanche / EVM sidechains)
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# 2. Set up  wallet using  private key
PRIVATE_KEY = "a77ab01ad2a7b3129adeafe47ac19b14a1c72cfca8130399225d0fe19d3e2217"  # make_wallet private key 
account = w3.eth.account.from_key(PRIVATE_KEY)
my_address = account.address

print(f"Using address: {my_address}")
print(f"Current balance: {w3.eth.get_balance(my_address)} Wei")

# 3. Contract Details provided in  assignment
CONTRACT_ADDRESS = "0x85ac2e065d4526FBeE6a2253389669a12318A412"

# Minimal ABI containing just the claim function
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

# 4. Generate a random nonce and try to claim an NFT
# The assignment mentions: tokenId = keccak256(nonce) % maxId
nonce = random.randint(1, 100000000)
print(f"Attempting to claim NFT with nonce: {nonce}")

# Build the transaction
nonce_count = w3.eth.get_transaction_count(my_address)
txn = contract.functions.claim(nonce).build_transaction({
    'chainId': 43113,  # Avalanche Fuji Chain ID
    'gas': 200000,
    'gasPrice': w3.eth.gas_price,
    'nonce': nonce_count,
})

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)

# Send the transaction
try:
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent! Hash: {tx_hash.hex()}")
    
    # Wait for the transaction to be mined
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("NFT successfully claimed! Transaction mined in block:", receipt.blockNumber)
    
except Exception as e:
    print(f"Claim failed (this can happen if the nonce was already taken): {e}")