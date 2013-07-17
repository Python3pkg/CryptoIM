import random

def generaterandom (n):
    r = ""
    rnd = random.SystemRandom()
    for i in range(n):
        f = rnd.random()
        if f >= 0.5:
            r = r + "1"
        else:
            r = r + "0"
    return r
# Generates random string of length n

def makeroundkey (key1,key2,strings):
    a=1
    b=2
    RoundKeys = []
    #Default Values

    key1 = int(key1,2)
    key2 = int(key2,2)
    #Formats key values into hex with proper length

    for i in range(16):
        strings[i] = int(strings[i].encode("hex"),16)
    #Puts strings into hex

    for i in range (16):
        if i%2==0:
            RoundKeys.append(key2^strings[i])
        elif i%2==1:
            RoundKeys.append(key1^strings[i])
        else:
            RoundKeys.append(key2^strings[i])
    #Sorts RoundKeys in right order
    return RoundKeys

def messagedivide (mess):
    messages = []
    for i in range (1,(len(mess)/8)+ 2):
        messages.append(mess[(8*i-8):(8*i)])
    return messages
#Divides messages into small pieces


Pk = int(raw_input("Insert your private cipher key: ")) #Privatekey
while Pk <(10000000):
    Pk = Pk + Pk
Pk = str(Pk)
Pk = Pk.encode("hex")
Pk = bin(int(Pk,16))[2:]
Pk = int(Pk,2)
#Makes 64 bit number

q = 1
while q == 1: # Infinite loop for infinite messages
    
    M = raw_input ("Your message: ")
    if M == "Break.Loop":
        break
    


    messages = messagedivide(M)
    while len(messages[-1]) < 8:
        messages[-1] = messages[-1] + " "
    #corrects lengths
    Output = []
    #prepares list for final output

    for w in range(len(messages)):

        RoundStrings = ["aeiouywg","chjmnbtr","loqd4850","zukhq4mn","uqwrifs2",
        "ctelmrdz","afjajc23","is2xafw8","svgw8e2r","hv2j39fs","jkdsg3e/","svls;wa4",
        "asfh29ce", "ajv29fsa", "ajf983fc", "xiw20dfs"]
        #Resets default value of RS
        
        K = int(generaterandom(64),2) #Generates random key
        key =bin(K^Pk) #creates specific key k 
        key = key.lstrip("0b")
        while len(key)<64:
            key = "0" + key
        #Fix to excluding 0 at the beginning (len(key) = 64)
        k1 = ""
        k2 = ""
        K = bin(K)
        K = K.lstrip("0b")
        while len(K)<64:
            K="0"+K
        for i in range (32):
            k1 = k1 + K[i]
            k2 = k2 + K[32+i]
        #Splits K into k1 + k2

        RoundKeys = makeroundkey(k1,k2,RoundStrings)
        f = []
        for i in range (16):
            RoundKeys[i] = int(bin(RoundKeys[i]),2)
        #Creates list of round keys
            
        Right = []
        Left = []
        #Creats lists for Feistel        
        

        for x in range (16):
            if x == 0:
                Hello = (messages[w][4:]).encode("hex")
                Right.append(int(Hello,16))
                Kitty = (messages[w][:4]).encode("hex")
                Left.append(int(Kitty,16))
                #Corrects format for xoring and sets input values
            else:
                Left.append(Right[x-1])
                Right.append(((RoundKeys[x]^Left[x])^Left[x-1]))
                #Does 16 rounds of Feistel network

       
        Right[15] = hex(Right[15])
        Left [15] = hex(Left[15])

        #Converts outputs of Feistel into hex values
        Right[15] = Right[15].rstrip("L").lstrip("0x")
        Left[15] = Left[15].rstrip("L").lstrip("0x")

        #Formating of hexadecimal values
        if len(Right[15])%2 != 0:
            Right[15] = "0"+Right[15]
        if len(Left[15])%2 != 0:
            Left[15] = "0"+Right[15]

        #Corrects lengths of Feistel outputs
        Right[15] = Right[15].decode("hex")
        Left[15] = Left[15].decode("hex")

        #Encodes them into plaintext
        key = str(key)
        key = int(key,2)
        key = hex(key).rstrip("L").lstrip("0x")
        if len(key)<16:
            key = "0"+key
        key = key.decode("hex")
        
        Output.append(Left[15]+Right[15])
        Output.append(key)
    Output = ",".join(Output)
    print Output
    #Output of ciphertext
    

    






        
