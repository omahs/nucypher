

from nucypher.blockchain.eth.agents import ContractAgency, TACoApplicationAgent
from tests.constants import TEST_ETH_PROVIDER_URI


def test_get_agent_with_different_registries(test_registry, agency_local_registry):
    # Get agents using same registry instance
    application_agent_1 = ContractAgency.get_agent(
        TACoApplicationAgent,
        registry=test_registry,
        provider_uri=TEST_ETH_PROVIDER_URI,
    )
    application_agent_2 = ContractAgency.get_agent(
        TACoApplicationAgent,
        registry=test_registry,
        provider_uri=TEST_ETH_PROVIDER_URI,
    )
    assert application_agent_2.registry == application_agent_1.registry == test_registry
    assert application_agent_2 is application_agent_1

    # Same content but different classes of registries
    application_agent_2 = ContractAgency.get_agent(
        TACoApplicationAgent,
        registry=agency_local_registry,
        provider_uri=TEST_ETH_PROVIDER_URI,
    )
    assert application_agent_2.registry == test_registry
    assert application_agent_2 is application_agent_1
