from etherscan import ETHERSCAN
from graph import GRAPH
from log import logger


if __name__ == "__main__":
    etherscan = ETHERSCAN()
    contract_address = "0x6Dce528d71814B3ead5FD2250a3a503121a7Bd5C"
    logger.info("Getting Deployer Address")
    deployer_address = etherscan.get_contract_creator(contract_address)
    if deployer_address:
        logger.info("Deployer address found")
    else:
        logger.info("No deployer address found")

    deployed_contracts = []
    if deployer_address:
        logger.info("Searching for all contracts deployed by deployer")
        deployed_contracts = etherscan.get_contracts_by_deployer(deployer_address)
    logger.info("Searching for top interacting addresses")
    top_interacting_addresses, top_interaction_count = etherscan.get_interacting_addresses(contract_address)
  
    logger.info("Building graph")
    graph = GRAPH()
    graph.build_deployer_and_deployed_contracts(deployer_address, deployed_contracts)
    graph.build_interacting_addresses(contract_address, top_interacting_addresses, top_interaction_count)
    logger.info("Generating list")
    graph.generate_list()
