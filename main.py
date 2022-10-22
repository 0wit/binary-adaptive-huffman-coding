import time
import os

# class representing node in a list

class Node:

    def __init__(self, symbol, index, left_child, right_child, count, code):
        self.symbol = symbol
        self.index = index
        self.left_child = left_child
        self.right_child = right_child
        self.count = count
        self.code = code


# symbol_list with escape_symbol
# initializing of buffer used to write bytes to output
# all_symbols variable is used for a quick control whether the input symbol is already in the tree(list)

escape_symbol = Node("", 0, None, None, 0, "")
symbol_list = [] #list of symbols
symbol_list.append(escape_symbol)
buffer = bytearray() #starting buffer
all_symbols = []

# method used to update code of nodes

def RecalculateTree(index, code):

    symbol_list[index].code = code

    if (symbol_list[index].left_child is not None and symbol_list[index].right_child is not None):

        RecalculateTree(symbol_list[index].left_child, code + "0")
        RecalculateTree(symbol_list[index].right_child, code + "1")
    
# method called after adding new symbol, increases symbol's occurence and checks whether a node with lesser count has also a lesser index
# if that's the cases nodes switch 

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

# epsilon is always the last symbol of list    

def ReturnCodeOfNewSymbol():
    return symbol_list[-1].code
    
# adding new symbol to the tree

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

# increase occurence of a symbol in the tree

def IncreaseOccurenceAndReturnCode(symbol):
    
    for x in range(len(symbol_list)):
        if (symbol_list[x].symbol == int.from_bytes(symbol, "big")):
            code = symbol_list[x].code
            UpdateTree(symbol_list[x].index)
            return code  

# symbols with their codes are written in bytes from bit_array to buffer

def WriteToBuffer(bit_array, buffer):

    strings = [str(integer) for integer in bit_array]
    a_string = "".join(strings)
    an_integer = int(a_string, 2)
    buffer.append(an_integer)

# method used to fill bit_array
# if bit_array is full, method writes it to the buffer
# if not, returns index (tracks current status)

def WriteStringToBitArrayThenBuffer(bit_array, j, string_to_encode):
    for i in range(len(string_to_encode)):                
                bit_array[j] = int(string_to_encode[i])
                j += 1
                if (j % 8 == 0 and j != 0):
                    WriteToBuffer(bit_array, buffer)
                    j = 0
    return j

# Main method used for compression. Loads input file, then keeps loading bytes of the file.
# If the symbol is new, it's added to all_symbols. The byte (number) is added to tree as a new symbol.

# Symbol encoding is written to output. However, most of the time it has to
# be written in 2 bytes and therefore split.

# bit_array with index that keeps track of current status is used for this.
# (varibale j is set to original value or 0)

# if the symbol is already in the tree, the occurence is increased and code written to output corresponds
# with the current code of the symbol in the tree
# state of bit_array is continuously checked (whether it's time to write it to buffer)

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
    
    # rest of the code  in bit_array + epsilon symbol encoding
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

# Main decompressing method. A tree is made. (Python list)
# New byte is loaded, it could be symbol already in a tree, new symbol or part of a symbol.
# The byte is read by bits. Method checks whether code it works with corresponds with code
# of epsilon symbol. If that is the case it means the symbol is new and the next byte (8 bits)
# is a new symbol. The new symbol could be split in 2 bytes.

# New symbol is saved as a byte not as a number unlike in compression.

# The symbol is repeated when the node has neither left nor right child.
# It's code is returned, occurence increased and the tree updated.

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
print("The compressed file is saved with the same name + '_compressed'," +
    " decompressed file is saved with the same name + _'uncompressed'.")

while (program_running):

    escape_symbol = Node("", 0, None, None, 0, "")
    symbol_list = [] #list of symbols
    symbol_list.append(escape_symbol)
    buffer = bytearray()
    all_symbols = []

    file_not_found = True

    while(file_not_found):
        user_input = input("Enter name of file with extension, that you want to compress: ")
        if os.path.isfile(user_input):            
            file_not_found = False

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
    print("Compression and decompression of your file lasted: " + str(round((end - start), 4)) + " seconds.")
    print("Original file size: " + str(original_size) + " bytes.\nAfter compressing it's: " + str(compressed_size) + " bytes.")
    print("File size difference: " + str(round(100 - (100 / original_size * compressed_size), 2)) + " %")

    print("Do you want to end the program?: Y/N")
    end_program = input()
    if (end_program.lower() == 'y'):
        program_running = False
