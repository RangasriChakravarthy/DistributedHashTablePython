from pprint import pprint
from typing import Dict, List
from math import pow


BITLENGTH = 8


class FingerTable:
    def __init__(self, node_id: int):
        self.finger_table = [None]*(BITLENGTH+1)  # Will host the list of nodes by index
        self.node_id = node_id

    def set(self, index: int, successor):
        # Provided in skeleton
        self.finger_table[index] = successor

    def get_item_from_finger_table(self, index):
        # Returns a node from an index of the finger table
        return self.finger_table[index]

    def pretty_print(self):
        print(" i | FT[i]\n")
        for i in range(1, BITLENGTH+1):
            print(f" {i} | {self.finger_table[i].get_id()}\n")


class Node:
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.node_pred = None
        self.node_succ = None
        self.finger_table = FingerTable(node_id)
        self.local_keys: Dict[int, int] = dict()

    def get_id(self):
        return self.node_id

    def set_pred(self, node):
        self.node_pred = node

    def get_pred(self):
        return self.node_pred

    def set_finger(self, index, node):
        self.finger_table.set(index, node)

    def get_finger(self, index):
        return self.finger_table.get_item_from_finger_table(index)

    def get_successor(self):
        return self.finger_table.get_item_from_finger_table(1)

    def find_successor(self, id_to_find):
        # function to help find the successor node for a given node_id
        # In chord algorithm, when a new node joins the network, we need to find its successor to properly link it
        # To find the successor, we'll first find the predecessor node from the ID that was passed
        # we then return the successor of the predecessor node
        n = self.find_prede(id_to_find)
        return n.get_finger(1)

    def find_prede(self, id_to_find):
        # Function from paper to get the closest predecessor node of any given ID to a node
        n = self
        while not between(n.get_id(), n.get_finger(1).get_id(), id_to_find, "right_inclusive"):
            # print("in loop")
            n = n.find_closest_preceding_finger(id_to_find)
        return n

    def find_closest_preceding_finger(self, id_to_find):
        for i in range(BITLENGTH, 1, -1):
            temp = self.get_finger(i)
            temp_id = temp.get_id()
            if between(self.node_id, id_to_find, temp_id, "exclusive"):
                return temp
        return self.get_successor()

    def update_finger_table_other_nodes(self, node, num: int) -> None:
        # Function to update finger table of all other nodes when a new node joins the chord network
        temp_id = node.get_id()
        if (self.node_id < self.get_finger(num).get_id()):
            if (self.node_id < temp_id < self.get_finger(num).get_id()):
                self.set_finger(num, node)
                p = self.get_pred()
                p.update_finger_table_other_nodes(node, num)

        elif self.node_id == self.get_finger(num).get_id():
            self.set_finger(num, node)
            p = self.get_pred()
            p.update_finger_table_other_nodes(node, num)

        elif temp_id > self.node_id or temp_id < self.get_finger(num).get_id():
            self.set_finger(num, node)
            p = self.get_pred()
            p.update_finger_table_other_nodes(node, num)

    def smaller_key(self, key_value_pairs, node_id):
        # Function to find all smaller keys in successor node for new node added top network
        keys_to_remove_from_orig_dict = []
        for k in self.local_keys:
            if k <= node_id:
                key_value_pairs.append([k, self.local_keys[k]])
                keys_to_remove_from_orig_dict.append(k)
        # Delete the keys to be moved from the original node
        for k in keys_to_remove_from_orig_dict:
            self.local_keys.pop(k)

    def join(self, node):
        if node:
            # valid node has been input
            successor = node.find_successor(self.node_id + 1)
            self.finger_table.set(1, successor)
            self.node_pred = successor.get_pred()
            self.node_succ = successor
            successor.set_pred(self)
            self.node_pred.set_finger(1, self)

            # Now proceed to update the finger table of the new node. What we know is that the first element of the
            # finger table is set to the successor of the new node in the network which we determined in the previous few
            # lines. Following this, we need to set the remaining entries of the new node finger table from the following:
            # 1. Finger table entries of the previous indices
            # 2. Entries in finger table of node n which is used to join the new node to the chord network

            for i in range(1, BITLENGTH):
                finger_entry = self.node_id + int(pow(2, i))

                if between(self.node_id, self.finger_table.get_item_from_finger_table(i).get_id(), finger_entry, "left_inclusive"):
                    self.finger_table.set(i+1, self.finger_table.get_item_from_finger_table(i))
                else:
                    next_node = node.find_successor(finger_entry % (pow(2, 8)))
                    self.finger_table.set(i+1, next_node)

             # update_other();
            for i in range(1, BITLENGTH+1):
                # print(i)
                candidate_check = self.node_id - pow(2, i-1)
                if candidate_check < 0:
                    # print(f"Candidate was negative {candidate_check}")
                    # Wrap around if candidate is negative
                    candidate_check += pow(2, BITLENGTH)
                    # print(f"Updated candidate to {candidate_check}")
                p = self.find_prede(candidate_check)
                p.update_finger_table_other_nodes(self, i)
        else:
            # First node entering network. Null value will be passed for node
            for i in range(1, BITLENGTH+1):
                self.finger_table.set(i, self)
            self.node_succ = self
            self.node_pred = self

        smaller_keys = []
        # Update smaller keys in function since lists are passed by reference in python
        self.node_succ.smaller_key(smaller_keys, self.node_id)

        print("-------------------------\n")
        print(f"Node {self.get_id()} joins.\n")
        # print(f"Finger Table of Node {self.get_id()} is as follow:\n")
        # self.finger_table.pretty_print()

        for i in range(len(smaller_keys)):
            curr_pair = smaller_keys[i]
            self.local_keys[curr_pair[0]] = curr_pair[1]
            print(f"Key {curr_pair[0]} is moved from successor Node {self.node_succ.get_id()} to Node {self.get_id()}")

        print("--------end join---------")

    def insert(self, dict_key, dict_value=None):
        # Insert k,v pair to local dict safely
        if between(self.node_pred.node_id, self.node_id, dict_key, "right_inclusive"):
            self.set_key_value_pair(dict_key, dict_value)
            print(f"Key {dict_key} was inserted into Node {self.node_id}")
        else:
            successor_node_to_key = self.find_successor(dict_key)
            successor_node_to_key.set_key_value_pair(dict_key, dict_value)
            print(f"Key {dict_key} was inserted into Node {successor_node_to_key.node_id}")

    def set_key_value_pair(self, dict_key: int, dict_value: int):
        # helper function to insert key value pairs
        """

        :param dict_key:
        :param dict_value:
        :return:
        """
        if dict_key in self.local_keys:
            print(f"Warning! Key {dict_key} already exists in node {self.node_id}. This request will be ignored")
        else:
            self.local_keys[dict_key] = dict_value

    def print_key_value_pairs(self):
        # to print the key-value pair that is present at each node
        print(f"------------Node id: {self.node_id}--------------")
        pprint(self.local_keys)

    def find(self, key_to_find):  # prof
        # Find key and if it exists, return the node
        # If the key satisfies condition: predecessor_id < key < curr_node_id, then the key should be present in
        # current nodes look up table
        # If the condition is not satisfied,call find successor for the given key. This should contain the required key.
        path = [self.node_id]
        if between(self.node_pred.node_id, self.node_id, key_to_find, "right_inclusive"):
            # Key should be present in current node
            if key_to_find not in self.local_keys:
                print(f"Key: {key_to_find} is not present in node {self.node_id}")
            else:
                print(f"Look-up result of key {key_to_find} from node {self.node_id} with path {path} value is "
                      f"{self.local_keys[key_to_find]}")
        else:
            # Find successor node where the key should be present
            node_candidate = self.find_successor(key_to_find)
            path.append(node_candidate.node_id)
            if key_to_find not in node_candidate.local_keys:
                print(f"Key: {key_to_find} is not present in node {node_candidate.node_id}")
            else:
                print(f"Look-up result of key {key_to_find} from node {self.node_id} with path {path} value is "
                      f"{node_candidate.local_keys[key_to_find]}")

    def remove(self, key_to_remove):
        #check if key is present in current node itself. If yes, remove it.
        if between(self.node_pred.node_id, self.node_id, key_to_remove, "right_inclusive"):
            if key_to_remove in self.local_keys:
                self.local_keys.pop(key_to_remove)
                print(f" Key {key_to_remove} has been removed from the Node {self.node_id}")
            else:
                print(f"Key {key_to_remove} not found in chord network")
        else:
            node_s = self.find_successor(key_to_remove)
            node_s.remove(key_to_remove)


def print_all_finger_tables(node_list: List[Node]):
    for node in node_list:
        print(f"Finger table of node {node.get_id()}")
        node.finger_table.pretty_print()


def find_all_keys_in_all_nodes(keys: List[int], nodes_to_search: List[Node]):
    for node in nodes_to_search:
        print(f"---------------------Node {node.node_id}--------------------------")
        for k in keys:
            node.find(k)
        print("\n")


def between(id_1: int, id_2: int, id_check: int, interval: str):
    if interval not in {'exclusive', 'left_inclusive', 'right_inclusive'}:
        print(f"operation {interval} is not supported. Please choose from the following: \n1.exclusive "
              f"\n2.left_inclusive \n3.right_inclusive")

    max_id = 2 ** BITLENGTH
    min_id = 0
    if interval == "exclusive":
        return (id_1 < id_2 and id_1 < id_check < id_2) or (id_1 > id_2 and ((id_1 < id_check <= max_id) or (
                min_id <= id_check < id_2))) or ((id_1 == id_2) and (id_check == id_1))
    elif interval == "left_inclusive":
        return (id_1 < id_2 and id_1 <= id_check < id_2) or (id_1 > id_2 and ((id_1 <= id_check <= max_id) or (
                min_id <= id_check < id_2))) or ((id_1 == id_2) and (id_check == id_1))
    elif interval == "right_inclusive":
        return (id_1 < id_2 and id_1 < id_check <= id_2) or (id_1 > id_2 and ((id_1 < id_check <= max_id) or (
                min_id <= id_check <= id_2))) or (id_1 == id_2)


if __name__=="__main__":
    n0 = Node(0)
    n1 = Node(30)
    n2 = Node(65)
    n3 = Node(110)
    n4 = Node(160)
    n5 = Node(230)
    n0.join(None)
    n1.join(n0)
    n2.join(n1)
    n3.join(n2)
    n4.join(n3)
    n5.join(n4)
    print_all_finger_tables([n0, n1, n2, n3, n4, n5])
    n0.insert(3, 3)
    n1.insert(200)
    n2.insert(123)
    n3.insert(45, 3)
    n4.insert(99)
    n2.insert(60, 10)
    n0.insert(50, 8)
    n3.insert(100, 5)
    n3.insert(101, 4)
    n3.insert(102, 6)
    n5.insert(240, 8)
    n5.insert(250, 10)
    n6 = Node(100)
    n6.join(n5)
    print_all_finger_tables([n0, n1, n2, n3, n4, n5, n6])
    n0.print_key_value_pairs()
    n1.print_key_value_pairs()
    n2.print_key_value_pairs()
    n3.print_key_value_pairs()
    n4.print_key_value_pairs()
    n5.print_key_value_pairs()
    n6.print_key_value_pairs()
    nodes = [n0, n1, n2, n6]
    keys_to_find = [3, 200, 123, 45, 99, 60, 50, 100, 101, 102, 240, 250]
    find_all_keys_in_all_nodes(keys_to_find, nodes)
    n0.remove(3)
    find_all_keys_in_all_nodes(keys_to_find, nodes)
