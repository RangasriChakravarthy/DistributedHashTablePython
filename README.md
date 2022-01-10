# DistributedHashTable
This project is an implementation of chord, a distributed hash table, for the course CSE250A.
Link to the paper is here: (https://conferences.sigcomm.org/sigcomm/2001/p12-stoica.pdf)

The main task of this project is to implement different functions of a node class. The keys and node identifiers are 8-bit. Hash functions (e.g. SHA-1
in Chord paper) are omitted in the project. The following are the 4 major functions implemented as part of this project:
1. join() : When a node join the DHT network, the node needs to build its own finger table for
routing purposes. To bootstrap this process, the node is provided with another node that
is already in the Chord network by some external mechanism. When a node joins, some keys should be migrated to it
as well. We will not consider multiple simultaneous joins in this project.

In Chord, each node maintains part of the distributed hash table. On condition that the
querying key is not maintained locally, the node needs to query the key from the Chord
network. Likewise, the node is also able to insert/remove keys in corresponding node.
Therefore, the following three functions are crucial too.

2. find() 
3. insert () 
4. remove()

All of these functions are tested in the main function.

Requirements to run the code:
1.	Python 3 installed in machine. (It was tested locally with Python 3.8.2)
2.	No extra packages required. All are met by python 3 installation

Navigate to the directory in which the code is stored using cd 

To run the code simply run:
python chord.py

References:
1. Professor Chen Qian’s lectures
2. Video explanation of the concepts of chord: https://www.youtube.com/watch?v=qqv4OJ5Lc4E
3. Lecture notes of Professor Steven Gordon: https://sandilands.info/sgordon/teaching/its413y12s2/unprotected/ITS413Y12S2L08-P2P.pdf

