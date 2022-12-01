import datetime as _dt
import hashlib as _hashlib
import json as _json

# example of data in side of X block
# new_product = {
#         "product_name": productname,
#         "product_ID": productId,
#         "ID_cert":certif,
#         "msg":msg,
#         "code_64":qrcode,
#         "x_index": len(blockChain.chain)     # this is redundant, just leave for now 
# }
# example of data in side of Y block
# new_transcation = {
#         "product_ID": productId,
#         "Seller": user1,
#         "Buyer": user2,
#         "x_index": 5,
#         "y_index":7
# }
class Blockchain:

    global xindex
    global yindex  
    xindex = 0 
    yindex = 0
    def __init__(self):
        self.chain = list()
        self.chain2 = list()
        genesis_data = {
            "product_name": "genesis block",
            "product_ID": "genesis block",
            "ID_cert":"genesis block",
            "msg":"genesis block",
            "code_64":"genesis block",
            "x_index": 0 
        }
        initial_block = self._create_block(
            data=genesis_data, proof=1, previous_hash="0", xindex=0,yindex=0
        )
        self.chain.append(initial_block)
        self.chain2.append([])

    def minex(self, data: dict) -> dict:      # change data type to dict
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        xindex = len(self.chain)
        proof = self._proof_of_work(
            previous_proof=previous_proof, xindex=xindex, yindex=yindex, data=data
        )
        previous_hash = self._hash(block=previous_block)
        block = self._create_block(
            data=data, proof=proof, previous_hash=previous_hash, xindex=xindex,yindex=yindex
        )
        self.chain.append(block)
        # self.chain2 = list()
        # initial_block = self.get_previous_block()
        # self.chain2.append(initial_block)
        # create a sub list for current x block, append it into chain2(idealy with have same index with its x block' index)
        # need to also add a empty sub-list for genesis block to keep index consistent, when genesis block init, added above at line 43
        self.chain2.append([])

        return block
        

    def miney(self, data: dict, x_index) -> dict:    # change data type to dict
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        yindex = len(self.chain2[x_index])
        xindex = x_index                             #len(self.chain) - 1  will pass in x-index
        proof = self._proof_of_work(
            previous_proof=previous_proof, xindex=xindex, yindex=yindex, data=data
        )
        previous_hash = self._hash(block=previous_block)
        block = self._create_block(
            data=data, proof=proof, previous_hash=previous_hash, xindex=xindex,yindex=yindex
        )
        # when append into chain2, first find the sub-list with index = x_index, then append the block at this sub-list
        # self.chain2.append(block)
        self.chain2[x_index].append(block)
        return block



    def _create_block(
        self, data: str, proof: int, previous_hash: str, xindex: int, yindex: int
    ) -> dict:
        block = {
            "x_index": xindex,  # change x-index to x_index
            "y_index": yindex,  # change y-index to y_index
            "timestamp": str(_dt.datetime.now()),
            "data": data,
            "proof": proof,
            "previous_hash": previous_hash,
        }

        return block
    

    def displayx(self) -> dict:
        return self.chain


    def displayy(self) -> dict:
        return self.chain2

    def search(self, x:str) -> dict:
        for key, value in self.chain2:
            print (key, value)

    def get_previous_block(self) -> dict:
        return self.chain[-1]

    def get_previous_block2(self) -> dict:
            return self.chain2[-1]

    def _to_digest(
        self, new_proof: int, previous_proof: int, xindex: int, yindex: int, data: dict   # change data to dict type to save more infor
    ) -> bytes:
        to_digest = str(new_proof ** 2 - previous_proof ** 2 + xindex + yindex) + str(data)
        # It returns an utf-8 encoded version of the string
        return to_digest.encode()

    def _proof_of_work(self, previous_proof: str, xindex: int, yindex: int, data: str) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            to_digest = self._to_digest(new_proof, previous_proof, xindex, yindex, data)
            hash_operation = _hashlib.sha256(to_digest).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def _hash(self, block: dict) -> str:
        """
        Hash a block and return the crytographic hash of the block
        """
        encoded_block = _json.dumps(block, sort_keys=True).encode()

        return _hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self) -> bool:
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            # Check if the previous hash of the current block is the same as the hash of it's previous block
            if block["previous_hash"] != self._hash(previous_block):
                return False

            previous_proof = previous_block["proof"]
            xindex, yindex, data, proof = block["x_index"],block["y_index"],block["data"], block["proof"]
            hash_operation = _hashlib.sha256(
                self._to_digest(
                    new_proof=proof,
                    previous_proof=previous_proof,
                    xindex=xindex,
                    yindex=yindex,
                    data=data,
                )
            ).hexdigest()

            if hash_operation[:4] != "0000":
                return False

            previous_block = block
            block_index += 1

        return True