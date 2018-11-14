#
# cryptorn - Tamamen hobi amaçlı eğlencesine denenmiştir.
#
import hashlib

PASSWORD = "Bismillah :)"

class Crypton(object):
    def __init__(self, password):
        self.password = password
        self.hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    def changeChar(self, achar, key):
        ch = ord(achar) ^ ord(key)
        return chr(ch)

    def crypt(self, _msg:str):
        cryptMsgTmp = []
        cryptMsg = ''
        i = 0
        for cha in _msg:
            cryptMsgTmp.append(self.changeChar(cha, self.hash[(i*i) % len(self.hash)]))
            i = i+1
        cryptMsg = ''.join(cryptMsgTmp)

        return cryptMsg
    
    def decrypt(self, _msg:str):
        return self.crypt(_msg)

if __name__ == '__main__':
    kripton = Crypton(PASSWORD)

    str_encoded = kripton.crypt("Selamünaleyküm hacı osman nabin nası gidii?(Giresun Ağzı)")
    str_decoded = kripton.decrypt(str_encoded)

    print(str_encoded)
    print(str_decoded)
