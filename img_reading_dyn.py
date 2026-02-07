#img_reading_dyn

from PIL import Image
import logging
import json
import Levenshtein
import re
import pytesseract
import cv2
import numpy as np
import bane_patch
import translator_search

#varrs needed
prefix_suffix_list = ['Laci','Nus','Ampi','Bin','Argi','Con','Pura','Ada','Manti','Tron','Geli','Do','Toxi','Tox','Igni','Pha','Vexi','Tio','Crita','Cron','Pleci','Nent','Acri','Tis','Visi','Ata','Exi','Cta','Croni','Dra','Conci','Nak','Para','Um','Magna','Ton','Insi','Cak','Sci','Sus','Arma','Tin','Forti','Us','Sati','Can','Lexi','Nok','Feva','Tak','Locti','Tor','Hexa','Dex','Deci','Des','Zeti','Mag','Hera','Lis','Tempi','Nem']
stat_names = ["Additional Combo Count Chance","Chance to Gain Combo Count","Fire Rate","Fire Rate(x2 for Bows)","Attack Speed","Ammo Maximum","Damage to Corpus","Damage to Grineer","Damage to Infested","Cold","Combo Duration","Critical Chance","Critical Chance (x2 for Heavy Attacks)","Critical Chance for Slide attack","Critical Damage","Damage","Melee damage","Electricity","Heat","Punch Through","Finisher Damage","Projectile Speed","Initial Combo","Impact","Magazine Capacity","Heavy Attack Efficiency","Multishot","Status Chance","Toxin","Puncture","Reload Speed","Range","Slash","Status Duration","Weapon Recoil","Zoom"]

def ocr_error(stats):
    stats = stats.strip()
    if stats[0] ==".":
        stats = stats[1:]
    if stats[0] =="%":
        stats = stats[1:]
    return stats

def find_match(stat):
    for stats in stat_names:
        if "infested" in stat.lower() and Levenshtein.jaro_winkler(stat.lower(), stats.lower()) > 0.921: 
            return stats
        elif Levenshtein.jaro_winkler(stat.lower(), stats.lower()) > 0.894 and "infested" not in stat.lower():            
            if "heavy" in stats.lower() and "slide" in stat.lower():
                continue
            return stats
        else:
            continue
    if stat.lower() == "pelmpact":
        return "Impact"
    if stat.lower() == "almpact":        
        return "Impact"
    if stat.lower() == "ampact":
        return "Impact"
    if stat.lower() == "plmpact":
        return "Impact"
    if stat.lower() == "pmpact":
        return "Impact"
    if stat.lower() == "3kcold":
        return "Cold"
    if stat.lower() == "3 cold":
        return "Cold"
    if stat.lower() == "4 heat":
        return "Heat"
    if stat.lower() == "BiToxin":
        return "Toxin"
    return stat

def grade_riven(image_riven):
    weapon_names = []
    with open("weapon_info.json") as json_file:
            weapon_info = json.load(json_file)
    for item in weapon_info:
        for weapons in weapon_info[item]['variants'].items():
            weapon_names.append(weapons[0].replace("Primary","").replace("Secondary","").strip())
    image_riven = np.array(image_riven)[:,:,::-1].copy()
    # image_riven = cv2.cvtColor(np.array(image_riven)[:,:,::-1].copy(),cv2.COLOR_BGR2RGB)
    image_riven_grayscape = cv2.cvtColor(image_riven, cv2.COLOR_BGR2GRAY)
    mr_img = cv2.imread("mr.png",0)
    reroll_img = cv2.imread("reroll.png",0)
    riven_symbol = cv2.imread("riven_symbol.png",0)
    bottom_riven = cv2.imread("bottom_riven.png",0)
    h = image_riven.shape[1]
    w = image_riven.shape[0]
    res_mr = cv2.matchTemplate(image_riven_grayscape, mr_img, cv2.TM_CCOEFF_NORMED)
    # print(res_mr)
    res_reroll = cv2.matchTemplate(image_riven_grayscape, reroll_img, cv2.TM_CCOEFF_NORMED)
    res_riven = cv2.matchTemplate(image_riven_grayscape, riven_symbol, cv2.TM_CCOEFF_NORMED)
    res_riven_bottom = cv2.matchTemplate(image_riven_grayscape, bottom_riven, cv2.TM_CCOEFF_NORMED)
    loc1 = np.where(res_mr >= 0.7)
    loc2 = np.where(res_reroll >= 0.7)
    loc3 = np.where(res_riven >= 0.7)
    loc4 = np.where(res_riven_bottom >= 0.5)
    # print(loc4)
    try:
        cv2.rectangle(image_riven, (0,loc3[0][0]),(w,0),(0, 0, 0), -1)
    except:
        print("failed riven symbol")
    
    # [top left],[bottom left],[bottom right],[topright]
    try:
        pts = np.array([[0,loc1[0][0]-5],[0,w],[h,w],[h,loc2[0][0]]], np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.fillPoly(image_riven,[pts],(0,0,0))
    except:
        print("didnt see both symbols")
    try:
        pts = np.array([[0,loc1[0][0]-5],[0,w],[h,w],[h,loc1[0][0]]], np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.fillPoly(image_riven,[pts],(0,0,0))
    except:
        print("didnt see mr symbol")
    image_riven = cv2.cvtColor(np.array(image_riven)[:,:,::-1].copy(),cv2.COLOR_BGR2RGB)
    # Image.fromarray(image_riven).show()
    image_text = [i for i in re.sub("[^A-Za-z0-9\+\-%()\n .]","",pytesseract.image_to_string(Image.fromarray(image_riven))).strip().splitlines() if i != ""]
    # print(image_text)
    rawnegstat, rawstat1, rawstat2, rawstat3, stat1stat, stat1val, stat2stat, stat2val, stat3stat, stat3val, negstat, negval = "", "", "", "", "", "", "", "", "", "", "", ""
    #negstat
    if "recoil" in image_text[-1].lower():
        if "-" in image_text[-1]:
            rawnegstat = ""
        if "+" in image_text[-1]:
            rawnegstat = image_text[-1]
            image_text.remove(image_text[-1])
    elif "slide attack" in image_text[-1].lower():
        rawnegstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
        image_text.remove(image_text[-1])
        image_text.remove(image_text[-1])
    elif bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1].lower() and ("-" in image_text[-1] or (bool(re.search(r'[x]\d+\.\d+', image_text[-1].lower())) and  bool(bane in image_text[-1].lower() for bane in ["corpus","grineer","infested"]))):
        rawnegstat = image_text[-1]
        image_text.remove(image_text[-1])
    elif "x2" in image_text[-1].lower() and bool(re.search(r'\d', image_text[-1])) == True and bool(re.search(r'\d', image_text[-2])) == True:
        rawnegstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
        image_text.remove(image_text[-1])
        image_text.remove(image_text[-1])
    elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True and ( "-" in image_text[-1] or (bool(re.search(r'[x]\d+\.\d+', image_text[-1].lower())) and  bool(bane in image_text[-1].lower() for bane in ["corpus","grineer","infested"]))):
        rawnegstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
        image_text.remove(image_text[-1])
        image_text.remove(image_text[-1])
    elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
        rawnegstat = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
        image_text.remove(image_text[-1])
        image_text.remove(image_text[-1])
    else:
        rawnegstat = ""

    #stat1
    try:
        if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
            rawstat1 = image_text[-1]
            image_text.remove(image_text[-1])
        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat1 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        elif "x2" in image_text[-1].lower() and bool(re.search(r'\d', image_text[-1])) == True and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat1 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat1 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        if "-" in rawstat1 and "recoil" not in rawstat1.lower():
            rawstat1 = ""
    except:
        rawstat1 = ""
        logging.info("stat 1 break")
    #stat2
    try:
        if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
            rawstat2 = image_text[-1]
            image_text.remove(image_text[-1])
        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat2 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        elif "x2" in image_text[-1].lower() and bool(re.search(r'\d', image_text[-1])) == True and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat2 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat2 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        if "-" in rawstat2 and "recoil" not in rawstat2.lower():
            rawstat2 = ""
    except:
        rawstat2 = ""
        logging.info("stat 2 break")
    try:
        if bool(re.search(r'\d', image_text[-1])) == True and "x2 for" not in image_text[-1]:
            rawstat3 = image_text[-1].replace("[","").replace("]","")
            image_text.remove(image_text[-1])
        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat3 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        elif "x2" in image_text[-1].lower() and bool(re.search(r'\d', image_text[-1])) == True and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat3 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        elif bool(re.search(r'\d', image_text[-1])) == False and bool(re.search(r'\d', image_text[-2])) == True:
            rawstat3 = str(image_text[-2]).replace("[","").replace("]","").replace(",","").replace("'","") + " " + str(image_text[-1]).replace("[","").replace("]","").replace(",","").replace("'","")
            image_text.remove(image_text[-1])
            image_text.remove(image_text[-1])
        if "-" in rawstat3 and "recoil" not in rawstat3.lower():
            rawstat3 = ""
    except:
        rawstat3 = ""
        logging.info("no stat 3 or stat 3 break")
    #extra parsing for ocr errors
    try:
        stat1 = ocr_error(rawstat1).strip()
    except:
        stat1 = rawstat1.strip()
        logging.info("stat1 ocr fix error")
    try:
        stat2 = ocr_error(rawstat2).strip()
    except:
        stat2 = rawstat2.strip()
        logging.info("stat2 ocr fix error")
    try:
        stat3 = ocr_error(rawstat3).strip()
    except:
        stat3 = rawstat3.strip()
        logging.info("stat3 ocr fix error")
    try:
        negstat = ocr_error(rawnegstat).strip()
    except:
        negstat = rawnegstat.strip()
        logging.info("negstat ocr fix error")

    #seperate stat names and values
    try:
        stat1val = re.findall("\-*\d+\.*\d*",stat1.split(" ")[0])[0]
        stat1stat = " ".join(stat1.split(" ")[1:])
    except:
        stat1val = "0"
        stat1stat = "[]"
        logging.info("stat1 failed")
    try:
        stat2val = re.findall("\-*\d+\.*\d*",stat2.split(" ")[0])[0]
        stat2stat = " ".join(stat2.split(" ")[1:])
    except:
        stat2val = "0"
        stat2stat = "[]"
        logging.info("stat2 failed")
    try:
        stat3val = re.findall("\-*\d+\.*\d*",stat3.split(" ")[0])[0]
        stat3stat = " ".join(stat3.split(" ")[1:])
    except:
        stat3val = "0"
        stat3stat = "[]"
        logging.info("stat3 failed")
    try:
        negval = re.findall("\-*\d+\.*\d*",negstat.split(" ")[0])[0]
        negstat = " ".join(negstat.split(" ")[1:])
    except:
        negval = "0"
        negstat = "[]"
        logging.info("negstat failed")                
    logging.info("parse info from riven image")
    #identifier to reduce duplication
    stat1stat = find_match(stat1stat)
    stat2stat = find_match(stat2stat)
    stat3stat = find_match(stat3stat)
    negstat = find_match(negstat)

    prefix_suffixs = []
    with open("prefix_suffix.json") as json_file:
        prefix_suffix = json.load(json_file)
    for i in [stat1stat, stat2stat, stat3stat]:
        try:
            prefix_suffixs.append(str(prefix_suffix[str(i).title()]['prefix']).lower())
            prefix_suffixs.append(str(prefix_suffix[str(i).title()]['suffix']).lower())
        except:
            prefix_suffixs.append("")
            prefix_suffixs.append("")
    image_text = "".join(image_text)
    for x in prefix_suffixs:
        if "vectis" not in image_text.lower():
            image_text = image_text.lower().replace(x, "")
    for i in weapon_names:
        if i.lower() in image_text.lower():
            weapon = i
            break
    stat1val, stat2val, stat3val, negval = str(bane_patch.front_to_back(stat1stat, stat1val)), str(bane_patch.front_to_back(stat2stat, stat2val)), str(bane_patch.front_to_back(stat3stat, stat3val)), str(bane_patch.front_to_back(negstat, negval))

    stat1stat, stat2stat, stat3stat, negstat = translator_search.translate_riven_tc(stat1stat), translator_search.translate_riven_tc(stat2stat), translator_search.translate_riven_tc(stat3stat), translator_search.translate_riven_tc(negstat)
    return [weapon, stat1val, stat1stat, stat2val, stat2stat, stat3val, stat3stat, negval, negstat]