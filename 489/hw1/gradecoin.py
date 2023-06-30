import json
import requests
import http.client
from Crypto.Cipher import AES, PKCS1_OAEP, PKCS1_v1_5
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from Crypto.Hash import SHA256, MD5, BLAKE2s
import base64
from Crypto.Cipher._mode_cbc import CbcMode
import time
import datetime
import jwt
import multiprocessing

# Create RSA key pair and save them to files


FINGERPRINT = "e5ed590ed68523b68a869b74564d824f56728d8b29af8dd4dcf1049dfa93c2e2"


def create_temp_key():
    """ Create a temporary key with 128 bits

    Returns:
        bytes: 128 bits key
    """
    return get_random_bytes(AES.block_size)

def create_iv():
    """ Create a random vector iv with 128 bits

    Returns:
        bytes: 128 bits iv
    """
    return get_random_bytes(AES.block_size)

def create_P_AR(student_id: str,one_time_pass : str, public_key : str):
    """ Create a json object P_AR with the following fields:

    Args:
        student_id (str): e.g. "e123456"
        one_time_pass (str): one time password
        public_key (str): public key in odtuclass

    Returns:
        json: P_AR dictionary
    """
    return json.dumps({
        "student_id" : student_id,
        "passwd" : one_time_pass,
        "public_key" : public_key
    })

def initialize_AES_cipher(temp_key : bytes, iv: bytes):
    """ Initialize AES cipher with temp_key and iv

    Args:
        temp_key (bytes): temporary key 128 bits
        iv (bytes): random vector 128 bits

    Returns:
        CbcMode: AES cipher
    """
    return AES.new(temp_key, AES.MODE_CBC, iv)

def encrypt_P_AR(cipher: CbcMode, P_AR : json):
    """
     Encrypt the serialized string of P_AR with 128 bit block AES in CBC mode
     with Pkcs7 padding using the temporary key (k_temp), the result is C_AR.
     Encode this with base64.

    Args:
        cipher (Crypto.Cipher._mode_cbc.CbcMode): AES cipher
        P_AR (json): P_AR dictionary

    Returns:
        bytes: encrypted P_AR
    """
    return base64.b64encode(cipher.encrypt(pad(P_AR.encode('utf-8'), AES.block_size, style='pkcs7')))

def encrypt_temp_key(temp_key : bytes, public_key : str):
    """ The temporary key you have picked k_temp is encrypted using RSA with OAEP padding scheme using SHA-256 with gradecoin_public_key, 
    giving us key_ciphertext. 
    Encode this with base64.

    Args:
        temp_key (bytes): temp_key 128 bits
        public_key (str): gradecoin public key

    Returns:
        bytes: encrypted temp_key
    """
    public_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
    return base64.b64encode(cipher_rsa.encrypt(temp_key))

def encode_iv_base64(iv: bytes):
    """ Encode iv with base64

    Args:
        iv (bytes): _description_
    
    Returns:
        bytes: encoded iv
    """

    return base64.b64encode(iv)

def create_auth_request(C_AR: bytes, iv : bytes, key_ciphertext: bytes):
    """ Serialize auth request

    Args:
        C_AR (bytes): encrypted P_AR
        iv (bytes): encoded iv 128 bits
        key (bytes): key_ciphertext
    """

    return json.dumps({
        "c" : C_AR.decode('utf-8'),
        "iv" : iv.decode('utf-8'),
        "key" : key_ciphertext.decode('utf-8')
    })

def create_transaction_body(source,target, amount, timestamp):
    """ Create a json object transaction with the following fields:

    Args:
        source (str): source student id
        target (str): target student id
        amount (int): amount of gradecoins
        timestamp (int): timestamp

    Returns:
        json: transaction dictionary
    """

    # There shouldn't be any whitespace or newlines in the serialized string.
    #The order of fields should be exactly as shown above.
    #All keys and string values must be enclosed with quotation marks (").
    body = json.dumps({
        "source":source,
        "target":target,
        "amount":amount,
        "timestamp":timestamp
    })

    # delete all whitespaces from body
    body = body.replace(" ", "")

    return body

def create_rsa_pair():
    """ Create a RSA key pair

    Returns:
        tuple: (private_key, public_key)
    """
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    # write them to files
    with open("private.pem", "wb") as f:
        f.write(private_key)
    with open("public.pem", "wb") as f:
        f.write(public_key)
    return private_key, public_key

def create_transaction_request(transaction_body: json, RSA_private_key):
    # create header
    header = {
        "alg" : "RS256",
        "typ" : "JWT"
    }

    # create payload
    payload = {
        "tha" : MD5.new(transaction_body.encode('utf-8')).hexdigest(),
        "iat" : int(time.time()),
        "exp" : int(time.time()) + 60
    }

    # create jwt
    jwt_obj = jwt.encode(payload, RSA_private_key, algorithm="RS256", headers=header)
    print(jwt_obj)
    
    return jwt_obj




def authenticate(student_id, gradecoin_public_key, one_time_pass, RSA_public_key, client):
    # create P_AR
    P_AR = create_P_AR(student_id, one_time_pass, RSA_public_key)

    # create temp key with 128 bits
    k_temp = create_temp_key()

    # create iv with 128 bits
    iv = create_iv()

    # initialize AES cipher
    cipher = initialize_AES_cipher(k_temp, iv)

    # encrypt P_AR
    C_AR = encrypt_P_AR(cipher, P_AR)

    # encrypt temp key
    key_ciphertext = encrypt_temp_key(k_temp, gradecoin_public_key)

    # encode iv
    iv_encoded = encode_iv_base64(iv)

    # create auth request
    auth_request = create_auth_request(C_AR, iv_encoded, key_ciphertext)

    # send auth request
    client.request("POST", "/register", auth_request)

    # get response
    response = client.getresponse()
    print(response.read().decode('utf-8'))
    print(response.headers)



def transaction(FINGERPRINT, target, amount, timestamp, RSA_private_key):
    # create transaction body
    transaction_body = create_transaction_body(FINGERPRINT,target, amount, timestamp)

    # create jwt token
    jwt_str = create_transaction_request(transaction_body, RSA_private_key)

    # send transaction request
    response = requests.post("https://gradecoin.xyz/transaction", data=transaction_body, headers={"Authorization" : "Bearer " + jwt_str})
    
    print(response.text)
    print(response.headers)

def block(RSA_private_key, hash_zeros, block_transaction_limit):
    # get request to get the all transactions available
    response = requests.get("https://gradecoin.xyz/transaction")

    # convert response to json
    response_json = json.loads(response.text)

    if block_transaction_limit > len(response_json.items()):
        print("block_transaction_limit is greater than the number of transactions available")
        return
    else:
        print("block creating...")
    
    transactions = []
    index = 1
    for key,value in response_json.items():
        # if source in value is my fingerprint then add and break
        if value["source"] == FINGERPRINT:
            transactions.append(key)
            break

    # add all transactions to the block except the one that I sent
    for key,value in response_json.items():
        if index == block_transaction_limit:
            break
        if key not in transactions:
            transactions.append(key)
            index += 1
    
    timestamp = datetime.datetime.now().isoformat()
    # create block body
    
    
    nonce = 0

    while True:
        block = json.dumps({
        "transaction_list" : transactions,
        "nonce": nonce,
        "timestamp": timestamp,
        }, separators=(',', ':'))

        block_hash = BLAKE2s.new(data=block.encode('utf-8')).hexdigest()

        if block_hash[:hash_zeros] == "0" * hash_zeros:
            print("Block hash: ", block_hash)
            print("FOUND!")
            break
        nonce += 1

    # Now we have a valid block hash, we can create a block request
    block_body = json.dumps({
        "transaction_list" : transactions,
        "nonce": nonce,
        "timestamp": timestamp,
        "hash": block_hash
    }, separators=(',', ':'))

    header = {
        "alg" : "RS256",
        "typ" : "JWT"
    }

    # create payload
    payload = {
        "tha" : block_hash,
        "iat" : int(time.time()),
        "exp" : int(time.time()) + 60
    }

    # create jwt
    jwt_str = jwt.encode(payload, RSA_private_key, algorithm="RS256", headers=header)


    # send block request
    response = requests.post("https://gradecoin.xyz/block", data=block_body, headers={"Authorization" : "Bearer " + jwt_str})

    print(response.text)
    print(response.headers)

def find_block_hash_multiprocessing(nonce_start, nonce_end, hash_zeros, transactions, timestamp):
    """ Finds a valid block hash using multiprocessing

    Args:
        nonce_start (int): start of the nonce range
        nonce_end (int): end of the nonce range
        hash_zeros (int): number of zeros that the hash should start with 
        transactions (list): list of transactions
        timestamp (timestamp): timestamp of the block

    Returns:
        nonce (int): nonce of the block
        block_hash (str): hash of the block
    """

    # iterate over the nonce range
    for nonce in range(nonce_start, nonce_end):
        # create block
        block = json.dumps({
            "transaction_list": transactions,
            "nonce": nonce,
            "timestamp": timestamp,
        }, separators=(',', ':'))

        # calculate block hash
        block_hash = BLAKE2s.new(data=block.encode('utf-8')).hexdigest()

        # check if block hash starts with hash_zeros number of zeros
        if block_hash[:hash_zeros] == "0" * hash_zeros:
            return nonce, block_hash

    # if no valid block hash in nonce range is found return None
    return None, None

def block_multiprocessing(RSA_private_key, hash_zeros, block_transaction_limit):
    # get request to get the all transactions available
    response = requests.get("https://gradecoin.xyz/transaction")

    # convert response to json
    response_json = json.loads(response.text)

    # if block_transaction_limit is greater than the number of transactions available exit
    if block_transaction_limit > len(response_json.items()):
        print("block_transaction_limit is greater than the number of transactions available")
        return
    else:
        print("starting block creation...")

    # unsigned 32 bit integer
    nonce_range = 2**32


    transactions = []
    index = 1

    # add my transaction as first item to the block
    for key, value in response_json.items():
        if value["source"] == FINGERPRINT:
            transactions.append(key)
            break

    # add all transactions to the block except the one that I sent
    for key, value in response_json.items():
        if index == block_transaction_limit:
            break
        if key not in transactions:
            transactions.append(key)
            index += 1

    # create timestamp
    timestamp = datetime.datetime.now().isoformat()

    # number of processes
    num_processes = multiprocessing.cpu_count()

    # chunk size
    chunk_size = nonce_range // num_processes

    # start timer
    start_time = time.time()

    # create pool of processes
    pool = multiprocessing.Pool(processes=num_processes)

    # create list of results
    results = [
        pool.apply_async(find_block_hash_multiprocessing, (start, start + chunk_size, hash_zeros, transactions, timestamp))
        for start in range(0, nonce_range, chunk_size)
    ]

    for result in results:
        nonce, block_hash = result.get()
        if nonce is not None:
            break

    if nonce is not None:
        print("Block hash:", block_hash)
        print("Nonce:", nonce)
        
        # Now we have a valid block hash, we can create a block request
        block_body = json.dumps({
            "transaction_list" : transactions,
            "nonce": nonce,
            "timestamp": timestamp,
            "hash": block_hash
        }, separators=(',', ':'))

        header = {
            "alg" : "RS256",
            "typ" : "JWT"
        }

        payload = {
            "tha" : block_hash,
            "iat" : int(time.time()),
            "exp" : int(time.time()) + 60
        }

        jwt_str = jwt.encode(payload, RSA_private_key, algorithm="RS256", headers=header)

        response = requests.post("https://gradecoin.xyz/block", data=block_body, headers={"Authorization" : "Bearer " + jwt_str})

        print(response.text)
        print(response.headers) 

        # end timer
        end_time = time.time()

        print("Time taken:", end_time - start_time)

        # kill all processes in the pool
        pool.terminate()
        return


def bot(RSA_private_key):
    BOT_1 = "5dcdedc9a04ea6950153c9279d0f8c1ac9528ee8cdf5cd912bebcf7764b3f9db"
    BOT_2 = "4319647f2ad81e83bf602692b32a082a6120c070b6fd4a1dbc589f16d37cbe1d"
    BOT_3 = "a4d9a38a04d0aa7de7c29fef061a1a539e6a192ef75ea9730aff49f9bb029f99"
    BOT_4 = "f44f83688b33213c639bc16f9c167543568d4173d5f4fc7eb1256f6c7bb23b26"
    SOURCE = FINGERPRINT

    while True:
        # get request to get the all transactions available
        response = requests.get("https://gradecoin.xyz/transaction")

        # convert response to json
        response_json = json.loads(response.text)

        # search transactions and try to find a transaction that is from me to one of the bots
        # if there is a transaction that is from me to one of the bots, do not send another transaction
        # if there is no transaction that is from me to one of the bots, send a transaction to one of the bots
        can_send = {"BOT_1" : True, "BOT_2" : True, "BOT_3" : True, "BOT_4" : True}
        for key, value in response_json.items():
            if value["source"] == SOURCE and value["target"] == BOT_1:
                can_send["BOT_1"] = False
            if value["source"] == SOURCE and value["target"] == BOT_2:
                can_send["BOT_2"] = False
            if value["source"] == SOURCE and value["target"] == BOT_3:
                can_send["BOT_3"] = False
            if value["source"] == SOURCE and value["target"] == BOT_4:
                can_send["BOT_4"] = False
        
        for key, value in can_send.items():
            if value == True:
                if key == "BOT_1":
                    timestamp = datetime.datetime.now().isoformat()
                    transaction(SOURCE,BOT_1,1,timestamp,RSA_private_key)
                if key == "BOT_2":
                    timestamp = datetime.datetime.now().isoformat()
                    transaction(SOURCE,BOT_2,1,timestamp,RSA_private_key)
                if key == "BOT_3":
                    timestamp = datetime.datetime.now().isoformat()
                    transaction(SOURCE,BOT_3,1,timestamp,RSA_private_key)
                if key == "BOT_4":
                    timestamp = datetime.datetime.now().isoformat()
                    transaction(SOURCE,BOT_4,1,timestamp,RSA_private_key)


        config_info = requests.get("https://gradecoin.xyz/config")

        hash_zeros = config_info.json()["hash_zeros"]
        block_transaction_limit = config_info.json()["block_transaction_count"]

        # try to solve block
        block_multiprocessing(RSA_private_key, hash_zeros, block_transaction_limit)


            





    





if __name__ == "__main__":

    client = http.client.HTTPSConnection("gradecoin.xyz")
    student_id = "e238102"
    gradecoin_public_key_path = "gradecoin.pub"
    one_time_pass = "Qk5aXqiEf+TVpQ0klkNK04ktjRjkNMx/"
    RSA_public_key_path = "public.pem"
    RSA_private_key_path = "private.pem"

    # read public key
    with open(gradecoin_public_key_path, "r") as f:
        gradecoin_public_key = f.read()

    with open(RSA_public_key_path, "r") as f:
        RSA_public_key = f.read()

    with open(RSA_private_key_path, "r") as f:
        RSA_private_key = f.read()

    #authenticate(student_id, gradecoin_public_key, one_time_pass, RSA_public_key, client)
    BOT_1 = "5dcdedc9a04ea6950153c9279d0f8c1ac9528ee8cdf5cd912bebcf7764b3f9db"
    BOT_2 = "4319647f2ad81e83bf602692b32a082a6120c070b6fd4a1dbc589f16d37cbe1d"
    BOT_3 = "a4d9a38a04d0aa7de7c29fef061a1a539e6a192ef75ea9730aff49f9bb029f99"
    BOT_4 = "f44f83688b33213c639bc16f9c167543568d4173d5f4fc7eb1256f6c7bb23b26"
    
    #transaction(FINGERPRINT=FINGERPRINT, target=BOT_1, amount=1, timestamp=datetime.datetime.now().isoformat(), RSA_private_key=RSA_private_key)
    #transaction(FINGERPRINT=FINGERPRINT, target=BOT_2, amount=1, timestamp=datetime.datetime.now().isoformat(), RSA_private_key=RSA_private_key)
    #transaction(FINGERPRINT=FINGERPRINT, target=BOT_3, amount=1, timestamp=datetime.datetime.now().isoformat(), RSA_private_key=RSA_private_key)
    #transaction(FINGERPRINT=FINGERPRINT, target=BOT_4, amount=1, timestamp=datetime.datetime.now().isoformat(), RSA_private_key=RSA_private_key)
    
    #block(RSA_private_key, hash_zeros, block_transaction_limit)

    #block_multiprocessing(RSA_private_key, hash_zeros, block_transaction_limit)

    bot(RSA_private_key)

    # close connection
    client.close()



