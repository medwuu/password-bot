def cryptMe(string):
    crypted_string = "/".join([hex(ord(x)) for x in string])
    return crypted_string


def encryptMe(crypred_string):
    string = crypred_string.split("/")
    string = [chr(int(x[2:], 16)) for x in string]
    string = "".join(string)
    return string