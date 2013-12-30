def encrypt(private_key, message):
    import random

    #Returns a decimal representation of n-bit long string
    def generaterandom(n):
        r = ""
        rnd = random.SystemRandom()
        for i in range(n):
            f = rnd.random()
            if f >= 0.5:
                r += "1"
            else:
                r += "0"
        r = int(r, 2)
        return r


    def makeroundkey(key1, key2, strings):
        a = 1
        b = 2
        RoundKeys = []
        #Default Values

        key1 = int(key1, 16)
        key2 = int(key2, 16)
        #Formats key values into hex with proper length

        for i in range(16):
            strings[i] = int(strings[i].encode("hex"), 16)
        #Puts strings into hex

        for i in range (16):
            if i % 2 == 0:
                RoundKeys.append(key2^strings[i])
            elif i % 2 == 1:
                RoundKeys.append(key1^strings[i])
            else:
                RoundKeys.append(key2^strings[i])
        #Sorts RoundKeys in right order
        return RoundKeys

    def messagedivide(mess):
        messages = []
        for i in range (1, (len(mess)/8) + 2):
            messages.append(mess[(8 * i - 8):(8 * i)])
        return messages
    #Divides messages into small pieces of 8 chars






    messages = messagedivide(message)
##    Splits message into 64 bit parts (8 ASCII)
##    characters, because algorithm uses only
##    64 bits
    private_key = int(private_key, 10)

    while private_key < 10000000:
        private_key = 2 * private_key

    private_key = str(private_key)
    private_key = private_key.encode("hex")
    private_key = private_key.lstrip("0x").rstrip("L")

    while len(private_key) < 16: ##In case it is too short
        private_key = "0" + private_key
    while len(private_key) > 16:   ##In case it is too long
        private_key = private_key[1:]

    private_key = int(private_key, 16)
    #Converts private key to 64 bit number in int

    for i in range(len(messages)):
        messages[i] = messages[i].encode("hex")
        messages[i] = messages[i].lstrip("0x").rstrip("L")
        if len(messages[i]) > 16:
            print "Error: Message at position " + i + " is too long."

        while len(messages[i]) < 16: ##If message is too short, pad it
            messages[i] = "0" + messages[i]

    for w in range(len(messages)):
        rndk = generaterandom(64) #Generates random key (64 bit)
        key = private_key^rndk
        key = hex(key).lstrip("0x").rstrip("L")
##        Key is generated by xoring
##        random key with private key

        if len(key) > 16:
            print "Error: Key at position " + w + " is too long."
        while len(key) < 16:
            key = "0" + key
        k1 = ""
        k2 = ""
        #Corrects length if needed and prepares strings for k1 and k2

        """
        for i in range (8):
            k1 = k1 + key[i]
            k2 = k2 + key[8+i]
        """
        #Toto je asi better:
        k1 += key[(len(key)/2):]
        k2 += key[:(len(key)/2)]
##        Splits the key into two 32 bit parts
##        because Feistel network needs round
##        keys which are 32 bit in length and
##        k1 and k2 are used in creating round keys

        RoundStrings = ["aeio", "chjm", "l0qd", "z4kh", "u4wr",
        "ctel", "afja", "is2x", "svgw", "hv2j", "jkds", "sv;s",
        "29ce", "v29f", "ajf9", "xiw2"]
##      Roundstrings are fixed to create roundkeys
##      They are put into loop so their value does
##      not overwrite with every round


        RoundKeys = makeroundkey(k1, k2, RoundStrings)

        Left = []
        Right = []
        Output = []
        #Prepares empty arrays for Feistel Network

        m1 += messages[w][:8]
        m2 += messages[w][8:]
##      Prepares empty strings for input values of m1
##      and m2 which have to be separated into 2 halfs
##      due to their length which is 64 bits and Feistel
##      input is 32 bits on each side
        #Splits the messages

        for x in range(17):
            if x == 0:
                Right.append(int(m2, 16))
                Left.append(int(m1, 16))
            else:
                Left.append(Right[x-1])
                #RoundKeys musi mat index [x-2], je to 16-dlhy array, nie 17 ako tento
                Right.append(Left[x-1]^Right[x-1]^RoundKeys[x-2])

##        Does 16 rounds of Feistel network
##        at x == 0 sets values of Right
##        and Left and on the others applies
##        Round keys in order to get final
##        output

        left_result = hex(Left[16]).lstrip("0x").rstrip("L")
        if len(left_result) > 8:
            print "Error: left_result at position " + w + " is too long."
        while len(left_result) < 8:
            left_result = "0" + left_result


        right_result = hex(Right[16]).lstrip("0x").rstrip("L")
        if len(right_result) > 8:
            print "Error: right_result at position " + w + " is too long."
        while len(right_result) < 8:
            right_result = "0" + right_result

        Output.append(left_result + right_result)
        Output.append(key)
        Output = ",".join(Output)
        return Output
