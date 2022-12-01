import datetime as dt
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

def create_new_keys():
    '''key generation fucntion'''
    orginal_key = ECC.generate(curve='P-256')
    private_key = orginal_key.export_key(format='DER')
    public_key = orginal_key.public_key().export_key(format='DER')
    print(private_key.hex())
    print(public_key.hex())
    # return orginal_key
    return {  
        'public_key':public_key, 
        'private_key':private_key
    }
def load_keys(key):
    '''key loading fucntion'''
    if type(key) == str:
        upload_key = ECC.import_key(bytearray.fromhex(key))
    else:
        upload_key = ECC.import_key(key)
    return upload_key

def signTransaction(data):
    '''
        key: private key
        data: the information about the transaction
    '''
    keys = ECC.generate(curve='P-256')
    str_data = str(data)
    print(str_data)
    message = bytes(str_data,'utf-8')
    h = SHA256.new(message)
    signer = DSS.new(keys, 'fips-186-3')
    signature = signer.sign(h)
    return signature.hex()

def verify(key,signature,msg):
    try:
        h = SHA256.new(msg)
        verifier = DSS.new(key, 'fips-186-3')
        verifier.verify(h,signature)  # only when it rasie value exception then the key is not authicated.
        return True
    except:
        return False

# create_new_keys()
# temp = bytearray.fromhex('308187020100301306072a8648ce3d020106082a8648ce3d030107046d306b0201010420a5b21484a53edc6c36f05799a042b79b65ed806d944b0228d167e3a4bdc705cda144034200044c57edeb00c1fc2ca22cd409e9a046f97cf6723be1efc1cc9209ee5df9b1f7368e494b3c518172e78324b9093fce507df83a2a2e29a296b91724765bcf383c62')
# print(temp)
# load_keys(temp)
# tempkey = ECC.import_key(b'\xcf\xc8\xc7\xeb&\x08\xe7\xe0\x11\x03\xc7`\xe8\xf1\x07:\n\x96x\x95\x04A9\xc5\xfd\xd6\x1dm\x04*\xc0\xce\xa6G\x0e\x0cl\xe1\xbe\xe3\n\xd0\x03\x81\x06\xd9\x92\x06\xe2y\xf4\xf1D\x9e7\xb0\xde\xfe!\x94\xa9\x02\x8a\x81')
# print(tempkey.export_key(format="DER").hex())
# aa1e8e71-636c-11ed-86cd-8cc681ecbcdc
# d717b342a073514caa8b3c7bec095f9a7af3adb262ef42bf73886b90577e699a
# 8cd7ea6e9b9c5f98c150e436b64399ad31d2c6462dca65fe2f068bf2bfec88bb52dc27ee2cdd73371dce5351deb4b1d21c003c939c263b67c5e350f0ca95910e

# verify(key=b'0Y0\x13\x06\x07*\x86H\xce=\x02\x01\x06\x08*\x86H\xce=\x03\x01\x07\x03B\x00\x04\x97\xf8\xc7\x17\xc9\x94K\x7f\x1ek\x00\xab\xb9\x1e\x17\x81QR +j&`:"\xcb{\x14\xd4P\xda\xf5\xbe\xb4V\xf4\xf5\xaf\xbf\xf7\x98h\xfb\x08\x9a!P\x9a\xc6\xda\xb4\xee\xa1b\xa9J1\x85\xb2\xbe\x06\xbep\x97',
#     signature=b'\xcf\xc8\xc7\xeb&\x08\xe7\xe0\x11\x03\xc7`\xe8\xf1\x07:\n\x96x\x95\x04A9\xc5\xfd\xd6\x1dm\x04*\xc0\xce\xa6G\x0e\x0cl\xe1\xbe\xe3\n\xd0\x03\x81\x06\xd9\x92\x06\xe2y\xf4\xf1D\x9e7\xb0\xde\xfe!\x94\xa9\x02\x8a\x81',
#     msg=b'f07a5ca3-636d-11ed-b944-8cc681ecbcdc this is test ex information')