import networkx as nx
import pandas as pd

class GRAPH:
    def __init__(self):
        self.__G = nx.DiGraph()

    def build_deployer_and_deployed_contracts(self, contract_creator_address, deployed_contracts):
        """
        Build the relationship deployer address and deployed contracts nodes

        Args:
            contract_creator_address (str): Smart Contract Creator Address
            deployed_contracts dict[str, str]: A dictionary mapping contract addresses to their contract names.
        
        Returns:
            None
        """

        deployer = contract_creator_address.lower()

        # If deployer address in gprah, add Deployer label to the existing label
        if deployer in self.__G:
            cur_list = self.__G.nodes[deployer].get('label', set())
            cur_list.add('Deployer')
            self.__G.nodes[deployer]['label'] = cur_list
        # Create a new node and label Deployer to it
        else:
            self.__G.add_node(deployer, label = {'Deployer'})
        
        # Add contract address node to the graph with deployer and contract name details
        for contract in deployed_contracts:
            if contract not in self.__G:
                contract = contract.lower()
                self.__G.add_node(contract, label={'Contract'}, deployer=deployer, contract_name=deployed_contracts[contract])
                self.__G.add_edge(deployer, contract, relationship={"d"})
                
        return None

    def build_interacting_addresses(self, deployed_contracts, interacting_addresses, top_interacting_addresses_count):
        """
        Build the relationship between deployed contracts and interacting adrress nodes

        Args:
            deployed_contracts dict[str, str]: A dictionary mapping contract addresses to their contract names.
            interacting_addresses list[str]: list of top interacting addresses
            top_interacting_addresses_count (int): The count of interactions for the top interacting address
        
        Returns:
            None
        """

        deployed_contracts = deployed_contracts.lower()
        for interacting_address in interacting_addresses:
            interacting_address = interacting_address.lower()
            # If interacting address node already in graph add Interacting to the label
            if interacting_address in self.__G:
                cur_list = self.__G.nodes[interacting_address].get('label', set())
                cur_list.add('Interacting')
                self.__G.nodes[interacting_address]['label'] = cur_list
            # Else create a new node with label Interacting
            else:
                self.__G.add_node(interacting_address, label=['Interacting'], address=interacting_address)

            # Edge
            current_relationship = self.__G[interacting_address][deployed_contracts].get('relationship', set())
            # Add i for relationship to mark the edge as Interacting
            current_relationship.add("i")
            nx.set_edge_attributes(self.__G, {(interacting_address, deployed_contracts): {'relationship': current_relationship}})
                
        # Add information on top_interacting_addresses_count and top_interacting_addresses information to the deployed contract node
        self.__G.nodes[deployed_contracts]['count'] = top_interacting_addresses_count
        self.__G.nodes[deployed_contracts]['top_interacting_addresses'] = interacting_addresses

        return None
    
    def generate_list(self):
        """
        Build graph data into excel sheet data and save the file it to the desktop

        Args:
            None
        
        Returns:
            None

        Table Column
        Address - Address of Deployer, Interacting or Contract
        Type - Contact, Deployer, Interacting
        Contract Created - If address type is Deployer, the list of contract address deployed provided here
        Deployed By - If address is Contract, the deployer address provided here
        Contract Name - If address is Contract, the name of contract provided here
        Top Interactor Address - If address is Contract, the list of interactor address provided here
        Top Interactor Count - If address is Contract, the top interaction count provided here
        Top Interacting Addresses - List of address where current node is top interactor

        """

        address, node_type, created_contract, deployer = [], [], [], []
        contract_name, top_interactor_address, top_interactor_count = [], [], []
        top_interacting_addresses = []

        nodes = nx.nodes(self.__G)
        attributes = {
            "label": nx.get_node_attributes(self.__G, "label"),
            "deployer": nx.get_node_attributes(self.__G, "deployer"),
            "contract_name": nx.get_node_attributes(self.__G, "contract_name"),
            "count": nx.get_node_attributes(self.__G, "count"),
            "top_interacting_addresses": nx.get_node_attributes(self.__G, "top_interacting_addresses")
        }
        edges_relationship = nx.get_edge_attributes(self.__G, "relationship")

        for node in nodes:
            address.append(node)
            label = ",".join(attributes["label"].get(node, ""))
            node_type.append(label)

            deployer_val, contract_name_val = None, None
            top_interactor_address_val, top_interactor_count_val = None, None
            created_contract_val, top_interacting_addresses_val = None, None

            if "Contract" in label:
                deployer_val = attributes["deployer"].get(node)
                contract_name_val = attributes["contract_name"].get(node)
                top_interactor_address_val = ",".join(attributes["top_interacting_addresses"].get(node, [])) or None
                top_interactor_count_val = attributes["count"].get(node)

            elif "Deployer" in label:
                contracts, interactors = [], []
                for edge in nx.edges(self.__G, node):
                    relationship = edges_relationship.get(edge)
                    if "d" in relationship:
                        contracts.append(edge[1])
                    if "i" in relationship:
                        interactors.append(edge[1])
                created_contract_val = ",".join(contracts) or None
                contract_name_val = ",".join(attributes["contract_name"].get(c) for c in contracts) or None
                top_interacting_addresses_val = ",".join(interactors) or None

            else:  
                interactors = [edge[1] for edge in nx.edges(self.__G, node) if "i" in edges_relationship.get(edge)]
                top_interacting_addresses_val = ",".join(interactors) or None

            deployer.append(deployer_val)
            created_contract.append(created_contract_val)
            contract_name.append(contract_name_val)
            top_interactor_address.append(top_interactor_address_val)
            top_interactor_count.append(top_interactor_count_val)
            top_interacting_addresses.append(top_interacting_addresses_val)

            df = pd.DataFrame({'Address': address, 'Type': node_type, "Contract Created": created_contract, "Deployed By":deployer, 
                  "Contract Name": contract_name, "Top Interactor Address": top_interactor_address, "Top Interactor Count": top_interactor_count,
                  "Top Interacting Addresses":top_interacting_addresses})

            file_path = '~/Desktop/graph_data2.xlsx'
            df.to_excel(file_path, index=False)           