import os
import rsa
import base64
from urllib.parse import quote_plus

def sign(data):
    privateKey = _load_private_key()
    signBytes = rsa.sign(data.encode(), privateKey, 'SHA-1')
    signStr = str(base64.b64encode(signBytes), 'utf-8')
    return quote_plus(signStr)


def verify(valueDict):
    signStr = valueDict['sign']
    del valueDict['sign']
    if valueDict.has_key('sign_type'):
        del valueDict['sign_type']
    tempStr = _compose_sign_str(valueDict)
    aliPayKey = _load_ali_pub_key()
    result = rsa.verify(tempStr, signStr, aliPayKey)
    return result 

def _load_private_key():
    keyfilePath = os.path.join(os.path.dirname(__file__), 'key', 'rsa_private_key.pem')
    with open(keyfilePath) as keyFile:
        return rsa.PrivateKey.load_pkcs1(keyFile.read().encode('latin_1'))
    
    
def _load_ali_pub_key():
    keyfilePath = os.path.join(os.path.dirname(__file__), 'key', 'ali_rsa_pub_key.pem')
    with open(keyfilePath) as keyFile:
        return rsa.PublicKey.load_pkcs1_openssl_pem(keyFile.read().encode('latin_1'))

def _compose_sign_str(valueDict):
    temp = []
    for key in valueDict:
        if not valueDict[key]:
            continue
        temp.append('{}="{}"'.format(key, valueDict[key]))
    tempStr = '&'.join(temp)
    return tempStr
