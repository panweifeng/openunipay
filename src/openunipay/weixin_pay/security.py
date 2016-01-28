import hashlib
from django.conf import settings

def sign(valueDict, unicodeEscapeKeySet=None):
    temp = []
    for key in sorted(valueDict):
        if not valueDict[key]:
            continue
        if unicodeEscapeKeySet and key in unicodeEscapeKeySet:
            valueDict[key] = valueDict[key].encode('unicode_escape')
        temp.append('{}={}'.format(key, valueDict[key]))
    temp.append('key=' + settings.WEIXIN['mch_seckey'])
    tempStr = '&'.join(temp)
    m = hashlib.md5()
    m.update(tempStr.encode())
    return m.hexdigest().upper()
