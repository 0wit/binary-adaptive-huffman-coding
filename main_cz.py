import time
import os

# Třída reprezentující uzel/prvek v listu.

class Node:

    def __init__(self, symbol, index, left_child, right_child, count, code):
        self.symbol = symbol
        self.index = index
        self.left_child = left_child
        self.right_child = right_child
        self.count = count
        self.code = code

# Na začátku se vytvoří symbol_list a vloží se do něj escape_symbol, inicializuje se buffer, pomocí
# kterého se pak zapisují jednotlivé byty do výstupního souboru.
# List all_symbols slouží pouze k rychlé kontrole, zda symbol už existuje v stromu/listu.

escape_symbol = Node("", 0, None, None, 0, "")
symbol_list = [] #list of symbols
symbol_list.append(escape_symbol)
buffer = bytearray() #Starting buffer
all_symbols = []

# Metoda, která se volá po tom, co se updatuje strom, aktualizuje všechny kódy uzlů.

def RecalculateTree(index, code):

    symbol_list[index].code = code

    if (symbol_list[index].left_child is not None and symbol_list[index].right_child is not None):

        RecalculateTree(symbol_list[index].left_child, code + "0")
        RecalculateTree(symbol_list[index].right_child, code + "1")
    
# Metoda, která se volá poté, co se přidá nový symbol/se zvýší výskyt symbolu. Pokud má nějaký uzel
# s menším index menší count, uzly se i s poduzly prohodí. (řešeno na úrovni indexů) 

def UpdateTree(index):
    
    while (index != 0):

        node_to_raise = symbol_list[index]        
        filter_list = []
        highest_value = 0

        for i in range(index):

            if (symbol_list[i].count == node_to_raise.count):
                filter_list.append(symbol_list[i])

        if (filter_list):
            highest_value = min(node.index for node in filter_list)

        if (highest_value ):

            if (highest_value != index - 1):

                tmp_node = Node(symbol_list[highest_value].symbol, 0, symbol_list[highest_value].left_child,
                symbol_list[highest_value].right_child, symbol_list[highest_value].count, symbol_list[highest_value].code)

                symbol_list[highest_value].symbol = node_to_raise.symbol
                symbol_list[highest_value].left_child = node_to_raise.left_child
                symbol_list[highest_value].right_child = node_to_raise.right_child

                symbol_list[index].symbol = tmp_node.symbol
                symbol_list[index].count = tmp_node.count
                symbol_list[index].left_child = tmp_node.left_child
                symbol_list[index].right_child = tmp_node.right_child

                index = highest_value

        symbol_list[index].count += 1
        
        for j in range(index):
            if (symbol_list[j].left_child == index or symbol_list[j].right_child == index):
                index = j
                break

    RecalculateTree(0, "")

# Epsilon je vždy posledním symbolem v listu, proto lze jeho kód získat takto    

def ReturnCodeOfNewSymbol():
    return symbol_list[-1].code
    
# Přidání nového symbolu do stromu.

def AddNewSymbolToTree(symbol):

    epsilon_symbol = symbol_list[-1]
    end_index = epsilon_symbol.index

    new_symbol = Node("", end_index, end_index + 1, end_index + 2, 0, epsilon_symbol.code)
    left_child = Node(symbol, end_index + 1, None, None, 0, epsilon_symbol.code + "0")
    right_child = Node("", end_index + 2, None, None, 0, epsilon_symbol.code + "1")

    symbol_list[-1] = new_symbol    
    symbol_list.append(left_child)
    symbol_list.append(right_child)  

    UpdateTree(left_child.index)

# Zvýšení četnosti symbolu ve stromu.

def IncreaseOccurenceAndReturnCode(symbol):
    
    for x in range(len(symbol_list)):
        if (symbol_list[x].symbol == int.from_bytes(symbol, "big")):
            code = symbol_list[x].code
            UpdateTree(symbol_list[x].index)
            return code  

# Symboly a jejich kódy se zapisují po 8 bitech (1 bajtu) z bit_array do bufferu

def WriteToBuffer(bit_array, buffer):

    strings = [str(integer) for integer in bit_array]
    a_string = "".join(strings)
    an_integer = int(a_string, 2)
    buffer.append(an_integer)

    #print(a_string)

# Naplňuje bit_array, pokud je plné, zapíše se do bufferu, pokud ne, vrátí se
# index, tzn. bit_array a zbytek lze zapsat, aktuální stav je udržován indexem.

def WriteStringToBitArrayThenBuffer(bit_array, j, string_to_encode):
    for i in range(len(string_to_encode)):                
                bit_array[j] = int(string_to_encode[i])
                j += 1
                if (j % 8 == 0 and j != 0):
                    WriteToBuffer(bit_array, buffer)
                    j = 0
    return j

# Hlavní metoda, která komprimuje vstup, načte input soubor, otestuje, zda je
# první výskyt symbolu, pokud ano, tak se symbol přidá do pole all_symbols.
#
# Z bytu se utvoří číslo, které se přidá do stromu jako nový symbol.

# Pak se zakódování symbolu (číslo bajtu) musí zapsat na výstup, ale tady pozor,
# protože index bit_array nemusí být 0, musí se zakódování symbolu většinou
# rozdělit do 2 bajtů.
#
# Pokud se tak stane, zapíše se bit_array do bufferu a rovnou se nastaví index
# na původní hodnotu, jinak se nastaví j na 0.

# Pokud se jedná už o několikátý výskyt symbolu, zvýší se četnost a vrátí se kód symbolu.
# Průběžně se kontroluje, jestli se má zapsat bit_array do bufferu.

def Compress(file_name, file_extension):

    string_to_encode = ""
    bit_array = [0] * 8
    j = 0

    print("Compressing...")

    with open(file_name + file_extension, "rb") as fh:

        element = fh.read(1)

        while element:

            new_symbol = not element in all_symbols

            if (new_symbol):

                all_symbols.append(element)
                string_to_encode = ReturnCodeOfNewSymbol()
                j = WriteStringToBitArrayThenBuffer(bit_array, j, string_to_encode)

                character_encoding = int.from_bytes(element, "big")                                
                AddNewSymbolToTree(character_encoding)
                character_encoding = bin(character_encoding)[2:]
                character_encoding = character_encoding.zfill(8)

                #print("Code of: " + element + " is: " + character_encoding)
                
                first_part = character_encoding[0:8-j]
                second_part = character_encoding[8-j:8]

                for k in range(len(first_part)):
                    bit_array[k+j] = int(first_part[k])

                WriteToBuffer(bit_array, buffer)
        
                original_j = j
                j = -1

                if (second_part):
                    for k in range(len(second_part)):
                        bit_array[k] = int(second_part[k])
                    j = original_j - 1

                j += 1

            else:
                string_to_encode = IncreaseOccurenceAndReturnCode(element)
                j = WriteStringToBitArrayThenBuffer(bit_array, j, string_to_encode)

            if (j % 8 == 0 and j != 0):
                WriteToBuffer(bit_array, buffer)
                j = 0

            element = fh.read(1)
    
    # Zbytek kódu, co se nemusí vlézt do 1 byte a zároveň zakódování epsilon symbolu.
    for i in range(8-j):
        bit_array[i+j] = "0"

    epsilon_code = ReturnCodeOfNewSymbol()
    j = WriteStringToBitArrayThenBuffer(bit_array, j, epsilon_code)

    if (j != 0):
        WriteToBuffer(bit_array, buffer)

    fh.close()
    with open(file_name + "_compressed", 'bw') as f:
        f.write(buffer)
    f.close()

# Hlavní metoda dekomprimace, taky se vytváří strom, respektive list.
# Načte se nový byte, může se jednat buď o zcela nový symbol, část nového
# symbolu, nebo rovnou celý nový symbol. Jede se po bitech z načteného bytu
# a průběžně se kontroluje, zda zrovna kód s kterým se pracuje odpovídá
# epsilon symbolu, jestliže ano, pak další byte bude nový symbol, často se,
# stejně jako v průběhu komprese může stát, že bude nový symbol uložen do
# 2 bytů, v tom případě je situace podobná jako v kompresi.
#
# Nový symbol se narozdíl od komprimace ukládá jako byte a ne jako číslo,
# chtěl jsem experimentovat s optimalizací, ale nedošlo na to.

# Pokud se výskyt symbolu opakuje, pozná se to podle toho, že se v kódu došlo
# do slepého bodu, uzel nemá ani pravého, ani levého potomka, tzn. symbol se
# opakuje, vrátí se jeho kód, zvýší četnost, strom se aktualizuje.

def Decompress(file_name, file_extension):
    
    print("Decompressing...")
    with open(file_name + "_compressed", "rb") as fh:
        
        element = fh.read(1)
        AddNewSymbolToTree(element)

        decoded_string = element
        new_symbol = element
        epsilon_symbol = "1"
        working_byte = ""
        current_index = 0

        while element:

            element = fh.read(1)
            new_byte = bin(int.from_bytes(element, "big"))[2:]
            new_byte = new_byte.zfill(8)
            
            #print("Byte, se kterým se pracuje: " + new_byte)

            for i in range(len(new_byte)):

                working_byte += new_byte[i]

                if (new_byte[i] == "0"):
                    current_index = symbol_list[current_index].left_child

                else:
                    current_index = symbol_list[current_index].right_child


                if (working_byte == epsilon_symbol):

                    if (i == 7):
                        new_symbol = bin(int.from_bytes(fh.read(1), "big"))[2:]
                    else:
                        new_symbol = new_byte[i+1:]
                        string_byte_to_fill = bin(int.from_bytes(fh.read(1), "big"))[2:]
                        string_byte_to_fill = string_byte_to_fill.zfill(8)
                        new_symbol += string_byte_to_fill[:i+1]
                        new_byte = string_byte_to_fill

                    new_symbol = int(new_symbol, 2)
                    new_symbol = new_symbol.to_bytes(1, "big")
                    
                    decoded_string += new_symbol
                    AddNewSymbolToTree(new_symbol)

                    epsilon_symbol = symbol_list[-1].code
                    working_byte = ""
                    current_index = 0

                elif (symbol_list[current_index].left_child is None and symbol_list[current_index].right_child is None):
                    
                    decoded_string += symbol_list[current_index].symbol
                    UpdateTree(current_index)

                    epsilon_symbol = symbol_list[-1].code
                    working_byte = ""
                    current_index = 0

        fh.close()
        f = open(file_name + "_uncompressed" + file_extension, "wb")
        f.write(decoded_string)
        f.close()


# Program runtime.

program_running = True

while (program_running):

    escape_symbol = Node("", 0, None, None, 0, "")
    symbol_list = [] #list of symbols
    symbol_list.append(escape_symbol)
    buffer = bytearray()
    all_symbols = []

    file_not_found = True
    while(file_not_found):
        user_input = input("Zadejte název souboru (i s příponou), který chcete zkomprimovat: ")
        if os.path.isfile(user_input):            
            file_not_found = False

    print("Zkomprimovaný soubor se uloží do souboru stejného názvu + '_compressed'," +
    " dekomprimovaný soubor se uloží do souboru stejného názvu a přípony + _'uncompressed'.") 

    file_name, file_extension = os.path.splitext(user_input)

    start = time.time()
    Compress(file_name, file_extension)
    escape_symbol = Node("", 0, None, None, 0, "")
    symbol_list = [] #list of symbols
    symbol_list.append(escape_symbol)
    buffer = bytearray()
    all_symbols = []
    Decompress(file_name, file_extension)
    end = time.time()

    original_size = os.path.getsize(user_input)
    compressed_size = os.path.getsize(file_name + "_compressed")
    print("Komprimace a dekomprimace souboru trvala: " + str(round((end - start), 4)) + " sekund.")
    print("Původní velikost souboru byla: " + str(original_size) + " bajtů.\nPo zkomprimování byla velikost: " + str(compressed_size) + " bajtů.")
    print("Soubor je menší o: " + str(round(100 - (100 / original_size * compressed_size), 2)) + " %")

    print("Chcete program ukončit?: Y/N")
    end_program = input()
    if (end_program.lower() == 'y'):
        program_running = False
