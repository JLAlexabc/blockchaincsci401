import pyqrcode as QR
from Crypto.Hash import SHA256
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
import uuid
# pip install pyqrcode
def create_QRcode(productID:str,userid): # this is a function design to create the QR code. A link is going to be used to within the parameters of this function and will generate into a QR code that can be scanned and the device that scans it will direct it to that said link.
    url = f'http://127.0.0.1:8000/u/viewproduct/productdetail/{userid}/{productID}'
    # http://127.0.0.1:8000/u/viewproduct/productdetail/0/c566d779-647d-11ed-b4df-8cc681ecbcdc
    img = QR.create(url,version=10) # add full url here
    return img.png_as_base64_str()

def create_productID(key='def',productInfo='this is test ex information'):
    '''key= private key form user'''

    proudctID = str(uuid.uuid1())

    content_str = proudctID+" "+productInfo
    content = bytes(content_str,encoding='utf-8')
    h = SHA256.new(content)
    signer = DSS.new(key, 'fips-186-3')
    signature = signer.sign(h)

    return [proudctID,signature.hex(),content_str]

def re_ceritifcate(product_id,key='def',productInfo='this is test ex information'):
    '''for a product be sold to other user, need to re-create the ceritifcate'''

    content_str = product_id+" "+productInfo
    content = bytes(content_str,encoding='utf-8')
    h = SHA256.new(content)
    signer = DSS.new(key, 'fips-186-3')
    signature = signer.sign(h)

    return [signature.hex(),content_str]
