import hashlib
from django.conf import settings

def sign(valueDict):
    temp = []
    for key in sorted(valueDict):
        if not valueDict[key]:
            continue
        temp.append('{}={}'.format(key, valueDict[key]))
    temp.append('key=' + settings.WEIXIN['mch_seckey'])
    tempStr = '&'.join(temp)
    m = hashlib.md5()
    m.update(tempStr.encode())
    return m.hexdigest().upper()
