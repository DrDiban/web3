# Hacken Assesment

1. Please install all the libariers in rquirements.txt
2. Create and .env file and add information on API_KEY = "XXXXXXXXXXXXXXXXXX" and 
WEB_URL = "https://api-sepolia.etherscan.io", for testing sepolia test network was used but if main net prefeered to be used please change the WEB_URL
3. etherscan.py contains the functions to obtains information about the deployer address, deployer other deployed contract and top interacting addreses and it's count based on a particular contract address
4. graph.py contains functions on creating the graph and exctracting all the data to an excel sheet
5. log.py is used for logging
5. main.py is where all the function are runned together i.e. the etherscan.py and graph.py
6. Table Column Details as follow
7. Address - Address of Deployer, Interacting or Contract
8. Type - Contact, Deployer, Interacting
9. Contract Created - If address type is Deployer, the list of contract addresses deployed provided here
10. Deployed By - If address is Contract, the deployer address provided here
11. Contract Name - If address is Contract, the name of contract provided here
12. Top Interactor Address - If address is Contract, the list of top interactor address provided here
13. Top Interactor Count - If address is Contract, the top interaction count provided here
14. Top Interacting Addresses - List of address where current node is top interactor

