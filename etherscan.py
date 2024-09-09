from dotenv import load_dotenv
import requests
import os

load_dotenv()

class ETHERSCAN:
    def __init__(self):
        self.__api_key = os.getenv("API_KEY")
        self.__web_url = os.getenv("WEB_URL")

    def get_contract_creator(self, contract_address):
        url = f"{self.__web_url}/api?module=contract&action=getcontractcreation&contractaddresses={contract_address}&apikey={self.__api_key}"
        response = requests.get(url)
        data = response.json()
  
        if data.get('status') == '1' and data.get('result'):
            return data['result'][0]['contractCreator'] 
        else:
            print("Error or no data found:", data.get('message'))
            return None
        
    def get_contracts_by_deployer(self, deployer_address):
        url = f"{self.__web_url}/api?module=account&action=txlist&address={deployer_address}&startblock=0&endblock=99999999&sort=asc&apikey={self.__api_key}"
        response = requests.get(url)
        data = response.json()
        deployed_contracts = {}

        for tx in data['result']:
            if tx['to'] == '':
                contract_name = self.get_contract_name(tx['contractAddress'])
                deployed_contracts[tx['contractAddress']] = contract_name

        return deployed_contracts

    def get_interacting_addresses(self, contract_address):
        url = f"{self.__web_url}/api?module=account&action=txlist&address={contract_address}&startblock=0&endblock=99999999&sort=asc&apikey={self.__api_key}"
        response = requests.get(url)
        data = response.json()
        top_interacting_addresses = []
        top_interaction_count = 0
        interacting_addresses_dic = {}

        for tx in data['result']:
            interacting_addresses = tx['from']
            if interacting_addresses and interacting_addresses!=contract_address:
                interacting_addresses_dic[interacting_addresses] = interacting_addresses_dic.get(interacting_addresses, 0) + 1
                cur_interacting_address_count = interacting_addresses_dic[interacting_addresses] 
                if cur_interacting_address_count > top_interaction_count:
                    top_interaction_count = cur_interacting_address_count
                    top_interacting_addresses = [interacting_addresses]
                elif cur_interacting_address_count == top_interaction_count:
                    top_interacting_addresses.append(interacting_addresses)
        return top_interacting_addresses, top_interaction_count
    
    def get_contract_name(self, contract_address):
        url = f"{self.__web_url}/api?module=contract&action=getsourcecode&address={contract_address}&apikey={self.__api_key}"
        response = requests.get(url)
        data = response.json()

        if data.get('status') == '1' and data.get('result'):
            contract_name = data['result'][0].get('ContractName')
            if contract_name:
                return contract_name
            else:
                return "No Name"
        else:
            return "No Name"


if __name__ == "__main__":

    etherscan = ETHERSCAN()
    print(etherscan.get_contract_creator("0x6Dce528d71814B3ead5FD2250a3a503121a7Bd5C"))
