import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

class GRAPH:
    def __init__(self):
        self.__G = nx.DiGraph()

    def build_deployer_and_deployed_contracts(self, deployer, deployed_contracts):
        
        deployer = deployer.lower()
        if deployer in self.__G:
            cur_list = self.__G.nodes[deployer].get('label', set())
            cur_list.add('Deployer')
            self.__G.nodes[deployer]['label'] = cur_list
        else:
            self.__G.add_node(deployer, label = {'Deployer'})
        
        for contract in deployed_contracts:
            contract = contract.lower()
            self.__G.add_node(contract, label={'Contract'}, deployer=deployer, contract_name=deployed_contracts[contract])
            self.__G.add_edge(deployer, contract, relationship={"d"})
                
        return None

    def build_interacting_addresses(self, deployed_contracts, interacting_addresses, top_interacting_addresses_count):
        deployed_contracts = deployed_contracts.lower()
        for address in interacting_addresses:
            address = address.lower()
            if address in self.__G:
                cur_list = self.__G.nodes[address].get('label', set())
                cur_list.add('Interacting')
                self.__G.nodes[address]['label'] = cur_list
            else:
                self.__G.add_node(address, label=['Interacting'], address=address)

            current_relationship = self.__G[address][deployed_contracts].get('relationship', set())
            if not isinstance(current_relationship, set):
                current_relationship = set(current_relationship)
            current_relationship.add("i")
            nx.set_edge_attributes(self.__G, {(address, deployed_contracts): {'relationship': current_relationship}})
                
        self.__G.nodes[deployed_contracts]['count'] = top_interacting_addresses_count
        self.__G.nodes[deployed_contracts]['top_interacting_addresses'] = interacting_addresses

        return None
    
    def generate_list(self):
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

            file_path = '~/Desktop/graph_data.xlsx'

            df.to_excel(file_path, index=False)