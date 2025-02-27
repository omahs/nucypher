import os

from nucypher_core.ferveo import DkgPublicKey

from nucypher.blockchain.eth.agents import CoordinatorAgent
from nucypher.blockchain.eth.registry import InMemoryContractRegistry
from nucypher.characters.lawful import Bob, Enrico
from nucypher.policy.conditions.lingo import ConditionLingo
from nucypher.utilities.logging import GlobalLoggerSettings

######################
# Boring setup stuff #
######################

LOG_LEVEL = "info"
GlobalLoggerSettings.set_log_level(log_level_name=LOG_LEVEL)
GlobalLoggerSettings.start_console_logging()

staking_provider_uri = os.environ["DEMO_L1_PROVIDER_URI"]
network = "lynx"

coordinator_provider_uri = os.environ["DEMO_L2_PROVIDER_URI"]
coordinator_network = "mumbai"

###############
# Enrico
###############

print("--------- Threshold Encryption ---------")

coordinator_agent = CoordinatorAgent(
    provider_uri=coordinator_provider_uri,
    registry=InMemoryContractRegistry.from_latest_publication(
        network=coordinator_network
    ),
)
ritual_id = 91  # got this from a side channel
ritual = coordinator_agent.get_ritual(ritual_id)
enrico = Enrico(encrypting_key=DkgPublicKey.from_bytes(bytes(ritual.public_key)))

print(
    f"Fetched DKG public key {bytes(enrico.policy_pubkey).hex()} "
    f"for ritual #{ritual_id} "
    f"from Coordinator {coordinator_agent.contract.address}"
)


conditions = {
    "version": ConditionLingo.VERSION,
    "condition": {
        "conditionType": "compound",
        "operator": "and",
        "operands": [
            {
                "conditionType": "rpc",
                "chain": 1,
                "method": "eth_getBalance",
                "parameters": ["0x210eeAC07542F815ebB6FD6689637D8cA2689392", "latest"],
                "returnValueTest": {"comparator": "==", "value": 0},
            },
            {
                "conditionType": "rpc",
                "chain": 137,
                "method": "eth_getBalance",
                "parameters": ["0x210eeAC07542F815ebB6FD6689637D8cA2689392", "latest"],
                "returnValueTest": {"comparator": "==", "value": 0},
            },
            {
                "conditionType": "rpc",
                "chain": 5,
                "method": "eth_getBalance",
                "parameters": ["0x210eeAC07542F815ebB6FD6689637D8cA2689392", "latest"],
                "returnValueTest": {"comparator": ">", "value": 1},
            },
            {
                "conditionType": "rpc",
                "chain": 80001,
                "method": "eth_getBalance",
                "parameters": ["0x210eeAC07542F815ebB6FD6689637D8cA2689392", "latest"],
                "returnValueTest": {"comparator": "==", "value": 0},
            },
        ],
    },
}

message = "hello world".encode()
threshold_message_kit = enrico.encrypt_for_dkg(plaintext=message, conditions=conditions)

print(f"Encrypted message: {bytes(threshold_message_kit).hex()}")

###############
# Bob
###############
print("--------- Threshold Decryption ---------")

bob = Bob(
    eth_provider_uri=staking_provider_uri,
    domain=network,
    coordinator_provider_uri=coordinator_provider_uri,
    coordinator_network=coordinator_network,
    registry=InMemoryContractRegistry.from_latest_publication(network=network),
)

bob.start_learning_loop(now=True)

cleartext = bob.threshold_decrypt(threshold_message_kit=threshold_message_kit)

print(bytes(cleartext).decode())
