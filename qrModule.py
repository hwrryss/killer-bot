import qrcode
import hashlib


def generateQr(name, code_word):
    prehash = name+code_word
    img = qrcode.make(hashlib.md5(prehash.encode()).hexdigest())
    img.save(prehash+ ".png")
    res = open(prehash + ".png", 'rb')
    return res

