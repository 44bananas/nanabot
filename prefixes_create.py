#prefixes_create

import translator_search
import json

def create_prefixes(stat1, stat2, stat3):
    #if stat from user = 1 then set it to none
    if stat1 == "1":
        stat1 = ""
    if stat2 == "1":
        stat2 = ""
    if stat3 == "1":
        stat3 = ""
    #open prefix_suffix
    with open("prefix_suffix.json") as json_file:
        prefix_suffix = json.load(json_file)
    print_message = ""
    #create a list of the stats translated
    stats = [translator_search.translate(stat1).title(),translator_search.translate(stat2).title(),translator_search.translate(stat3).title()]
    prefix = []
    suffix = []
    #get the prefixes/suffexes
    for y in stats:
        try:
            prefix.append(str(prefix_suffix[str(y).title()]['prefix']))
            suffix.append(str(prefix_suffix[str(y).title()]['suffix']))
        except:
            prefix.append("")
            suffix.append("")
    #check if its empty
    if prefix[0] == "" and suffix[0] == "" and prefix[1] == "" and suffix[1] == "" and prefix[2] == "" and suffix[2] == "":
        print("fucked")
    #check if its a single stat
    elif prefix[0] == "" and suffix[0] == "" and prefix[1] == "" and suffix[1] == "":
        print_message += str(prefix[2]) + "\n" + str(suffix[0]) + "\n"
    elif prefix[1] == "" and suffix[1] == "" and prefix[2] == "" and suffix[2] == "":
        print_message += str(prefix[0]) + "\n" + str(suffix[0]) + "\n"
    elif prefix[0] == "" and suffix[0] == "" and prefix[2] == "" and suffix[2] == "":
        print_message += str(prefix[1]) + "\n" + str(suffix[1]) + "\n"
    #check if its a dual stat
    elif prefix[0] == "" and suffix[0] == "":
        print_message += str(prefix[1]) + str(suffix[2]) + "\n"
        print_message += str(prefix[2]) + str(suffix[1]) + "\n"
    elif prefix[1] == "" and suffix[1] == "":
        print_message += str(prefix[0]) + str(suffix[2]) + "\n"
        print_message += str(prefix[2]) + str(suffix[0]) + "\n"
    elif prefix[2] == "" and suffix[2] == "":
        print_message += str(prefix[1]) + str(suffix[0]) + "\n"
        print_message += str(prefix[0]) + str(suffix[1]) + "\n"
    #check if all 3 arent empty
    elif (prefix[0] != "" and suffix[0] != "") and (prefix[1] != "" and suffix[1] != "") and (prefix[2] != "" and suffix[2] != ""):
        print_message += str(prefix[0]) + "-" + str(prefix[1]) + str(suffix[2]) + "\n"
        print_message += str(prefix[0]) + "-" + str(prefix[2]) + str(suffix[1]) + "\n"
        print_message += str(prefix[1]) + "-" + str(prefix[0]) + str(suffix[2]) + "\n"
        print_message += str(prefix[1]) + "-" + str(prefix[2]) + str(suffix[0]) + "\n"
        print_message += str(prefix[2]) + "-" + str(prefix[0]) + str(suffix[1]) + "\n"
        print_message += str(prefix[2]) + "-" + str(prefix[1]) + str(suffix[0]) + "\n"
    #if its not empty, add newlines
    if prefix != ["","",""]:
        print_message += "\n\n"
    return print_message.capitalize()