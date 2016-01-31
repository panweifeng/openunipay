import rsa
import base64
from django.conf import settings
from openunipay.ali_pay import logger

def sign(data):
    privateKey = _load_private_key(settings.ALIPAY['rsa_private_key_pem'])
    signBytes = rsa.sign(data.encode(), privateKey, 'SHA-1')
    signStr = str(base64.b64encode(signBytes), 'utf-8')
    return signStr

def verify(data, sign, pemKeyfile):
    sign = base64.b64decode(sign)
    pubKey = _load_public_key(pemKeyfile)
    result = False
    try:
        rsa.verify(data.encode(), sign, pubKey)
    except rsa.pkcs1.VerificationError:
        result = False
    else:
        result = True
    return result


def verify_ali_data(valueDict):
    logger.info('verifying data from ali')
    sign = valueDict['sign']
    # remove sign and sign_type
    del valueDict['sign']
    if 'sign_type' in valueDict:
        del valueDict['sign_type']
    # contact string need to verify
    temp = []
    for key in sorted(valueDict):
        if not valueDict[key]:
            continue
        temp.append('{}={}'.format(key, valueDict[key]))
    tempStr = '&'.join(temp)
    logger.info('string to verify:{}'.format(tempStr))
    return verify(tempStr, sign, settings.ALIPAY['ali_public_key_pem'])
    

def _load_private_key(pemKeyfile):
    with open(pemKeyfile) as keyFile:
        return rsa.PrivateKey.load_pkcs1(keyFile.read().encode('latin_1'))
    
def _load_public_key(pemKeyfile):
    with open(pemKeyfile) as keyFile:
        return rsa.PublicKey.load_pkcs1_openssl_pem(keyFile.read().encode('latin_1'))
    
