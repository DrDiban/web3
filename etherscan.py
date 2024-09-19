from dotenv import load_dotenv
import requests
import os
from log import logger
load_dotenv()

class ETHERSCAN:
    def __init__(self):
        # Initialize the API key for etherscan and the web url
        self.__api_key = os.getenv("API_KEY")
        self.__web_url = os.getenv("WEB_URL")

    def get_contract_creator(self, contract_address: str) -> str:
        """Gets the contract creator based on the contract address provided

        Args:
            contract_address (str): Smart Contract Address

        Returns:
            str: Smart Contract Creator Wallet Address, or None if not found
        """
        url = f"{self.__web_url}/api?module=contract&action=getcontractcreation&contractaddresses={contract_address}&apikey={self.__api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()

            # Check if status is successful and result exists
            if data.get('status') == '1' and isinstance(data.get('result'), list) and len(data['result']) > 0:
                return data['result'][0].get('contractCreator')

            else:
                logger.info(f"Error or no data found: {data.get('message')}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return None
        
    def get_contracts_by_deployer(self, contract_creator_address: str) -> dict[str, str]:
        """Gets all the contract addresses created by a contract creator.

        Args:
            contract_creator_address (str): Smart Contract Creator Address
        
        Returns:
            dict[str, str]: A dictionary mapping contract addresses to their contract names.
        """

        url = f"{self.__web_url}/api?module=account&action=txlist&address={contract_creator_address}&startblock=0&endblock=99999999&sort=asc&apikey={self.__api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
            data = response.json()

            if data.get('status') != '1' or not data.get('result'):
                logger.info(f"No valid transactions found for creator {contract_creator_address}: {data.get('message')}")
                return {}

            deployed_contracts = {}
            
            # Loop through transactions and find contract creation events
            for tx in data['result']:
                if tx.get('to') == '':  # This indicates a contract creation transaction
                    contract_address = tx.get('contractAddress')
                    if contract_address:
                        contract_name = self.get_contract_name(contract_address)
                        deployed_contracts[contract_address] = contract_name or "Unknown Contract"

            return deployed_contracts

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve contracts for {contract_creator_address}: {e}")
            return {}

    def get_top_interacting_addresses_and_count(self, contract_address: str) -> tuple[list[str], int]:
        """Gets the top interacting addresses and the total interaction count.

        Args:
            contract_address (str): Smart Contract Address
        
        Returns:
            tuple[list[str], int]: 
                - list of top interacting addresses
                - the count of interactions for the top address
        """
        url = f"{self.__web_url}/api?module=account&action=txlist&address={contract_address}&startblock=0&endblock=99999999&sort=asc&apikey={self.__api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            data = response.json()

            if data.get('status') != '1' or not data.get('result'):
                logger.info(f"No valid transactions found for contract {contract_address}: {data.get('message')}")
                return [], 0

            interacting_addresses_dic = {}
            top_interacting_addresses = []
            top_interaction_count = 0

            # Loop through transactions and track interacting addresses
            for tx in data['result']:
                interacting_address = tx.get('from')
                if interacting_address and interacting_address != contract_address:
                    interacting_addresses_dic[interacting_address] = interacting_addresses_dic.get(interacting_address, 0) + 1
                    cur_interaction_count = interacting_addresses_dic[interacting_address]

                    # Track the address with the highest interaction count
                    if cur_interaction_count > top_interaction_count:
                        top_interaction_count = cur_interaction_count
                        top_interacting_addresses = [interacting_address]
                    # If the cur count interaction address matches with top address count append it to the list
                    elif cur_interaction_count == top_interaction_count:
                        top_interacting_addresses.append(interacting_address)

            return top_interacting_addresses, top_interaction_count

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve interacting addresses for {contract_address}: {e}")
            return [], 0
    
    def get_contract_name(self, contract_address: str) -> str:
        """Gets the contract name based on the provided contract address.

        Args:
            contract_address (str): Smart Contract Address
        
        Returns:
            str: Contract name or "No Name" if not found
        """
        url = f"{self.__web_url}/api?module=contract&action=getsourcecode&address={contract_address}&apikey={self.__api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an error for bad HTTP responses
            data = response.json()

            if data.get('status') == '1' and data.get('result'):
                contract_name = data['result'][0].get('ContractName')
                if contract_name:
                    return contract_name
                else:
                    logger.info(f"No contract name found for address {contract_address}")
                    return "No Name"
            else:
                logger.info(f"Error or no data found for contract {contract_address}: {data.get('message')}")
                return "No Name"

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve contract name for {contract_address}: {e}")
            return "No Name"


if __name__ == "__main__":

    # For testing functions
    etherscan = ETHERSCAN()

    contract_address = "0x6Dce528d71814B3ead5FD2250a3a503121a7Bd5C"
    logger.info("Finding contract creator")
    contract_creator_address = etherscan.get_contract_creator('0x6Dce528d71814B3ead5FD2250a3a503121a7Bd5C')
    logger.info(f"Contract creator address: {contract_creator_address} for contract {contract_address}")

    logger.info("Finding all contract developed by deployer")
    deployed_contracts = etherscan.get_contracts_by_deployer(contract_creator_address)
    logger.info(f"Contract developed by deployer: {deployed_contracts} for deployer {contract_creator_address}")

    logger.info("Finding the top interacting address and the count")
    top_interacting_addresses, top_interaction_count = etherscan.get_top_interacting_addresses_and_count(contract_address)
    logger.info(f"Top interacting addresse: {top_interacting_addresses} and count: {top_interaction_count} for contract address {contract_address}")


