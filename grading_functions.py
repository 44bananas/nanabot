#grading_functions

import json
import re
import translator_search

kitgun_list = ["Sporelacer","Rattleguts","Vermisplicer","Catchmoon","Gaze","Tombfinger"]

#open dispos
with open("rifle_dispos.txt") as json_file:
    rifle_dispos = json.load(json_file)
with open("pistol_dispos.txt") as json_file:
    pistol_dispos = json.load(json_file)
with open("melee_dispos.txt") as json_file:
    melee_dispos = json.load(json_file)
with open("shotgun_dispos.txt") as json_file:
    shotgun_dispos = json.load(json_file)
with open("archgun_dispos.txt") as json_file:
    archgun_dispos = json.load(json_file)
with open("kitgun_dispos.txt") as json_file:
    kitgun_dispos = json.load(json_file)

#open base stats
with open("rifle_base.txt") as json_file:
    rifle_base = json.load(json_file)
with open("pistol_base.txt") as json_file:
    pistol_base = json.load(json_file)
with open("melee_base.txt") as json_file:
    melee_base = json.load(json_file)
with open("shotgun_base.txt") as json_file:
    shotgun_base = json.load(json_file)
with open("archgun_base.txt") as json_file:
    archgun_base = json.load(json_file)

#returns grades in a dict
def get_grade(weapon_name, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat):
    grades_dict = {}
    number_of_filters = 0
    for weapon in weapon_name:
        weapon = str(weapon).title()
        if is_weapon_in(weapon) == True:
            grades = get_grade_varriants(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat)
            if grades != []:
                for x in grades_dict:
                    number_of_filters = x
                number_of_filters = int(number_of_filters) + 1
                grades_dict.update({str(number_of_filters):{"weapon": weapon.title(), "pos1": grades[0], "pos2": grades[1], "pos3": grades[2], "neg": grades[3]}})
        #check if weapon is kitgun
        if weapon in kitgun_list:
            #grab secondary stats
            (stats, dispo) = get_kitgun_dipos_and_base_stats_secondary(weapon)
            grades = grade_weapon(stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat,stats, dispo)
            if grades != []:
                for x in grades_dict:
                    number_of_filters = x
                number_of_filters = int(number_of_filters) + 1
                grades_dict.update({str(number_of_filters):{"weapon": weapon.title(), "pos1": grades[0], "pos2": grades[1], "pos3": grades[2], "neg": grades[3]}})
            #grab primary stats
            (stats, dispo) = get_kitgun_dipos_and_base_stats_primary(weapon)
            grades = grade_weapon(stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat,stats, dispo)
            if grades != []:
                for x in grades_dict:
                    number_of_filters = x
                number_of_filters = int(number_of_filters) + 1
                grades_dict.update({str(number_of_filters):{"weapon": weapon.title(), "pos1": grades[0], "pos2": grades[1], "pos3": grades[2], "neg": grades[3]}}) 
    return grades_dict

#get dispo and base stats for kitguns secondary
def get_kitgun_dipos_and_base_stats_secondary(weapon):
    weapon = str(weapon).title()
    if weapon == "Catchmoon":
        return (pistol_base,kitgun_dispos[weapon]['Secondary'])
    elif weapon in kitgun_list and weapon != "Catchmoon":
        return (pistol_base,kitgun_dispos[weapon]['Secondary'])
    
#get dispo and base stats for kitguns primary
def get_kitgun_dipos_and_base_stats_primary(weapon):
    weapon = str(weapon).title()
    if weapon == "Catchmoon":
        return (pistol_base,kitgun_dispos[weapon]['Primary'])
    elif weapon in kitgun_list and weapon != "Catchmoon":
        return (shotgun_base,kitgun_dispos[weapon]['Primary'])

def get_varriants(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat):
    weapon = str(weapon).title()
    stat1name = str(stat1name).lower()
    stat2name = str(stat2name).lower()
    stat3name = str(stat3name).lower()
    negstat = str(negstat).lower()
    #weapon names to check
    kuva_varriant = "kuva " + weapon
    prime_varriant = weapon + " prime"
    tenet_varriant = "tenet " + weapon
    prisma_varriant = "prisma " + weapon
    wraith_varriant = weapon + " wraith"
    synoid_varriant = "synoid " + weapon
    vandal_varriant = weapon + " vandal"
    mk1_varriant = "mk1-" + weapon
    sancti_varriant = "sancti " + weapon
    carmine_varriant = "carmine " + weapon
    telos_varriant = "telos " + weapon 
    rakta_varriant = "rakta " + weapon
    secura_varriant = "secura " + weapon
    vaykor_varriant = "vaykor " + weapon
    mara_varriant = "mara " + weapon
    if weapon == "Afuris":
        dex_varriant = "Dex Furis"
        weapon_list = [dex_varriant,kuva_varriant, prime_varriant, tenet_varriant, prisma_varriant, wraith_varriant, synoid_varriant, vandal_varriant, mk1_varriant, sancti_varriant, carmine_varriant, telos_varriant, rakta_varriant, secura_varriant, vaykor_varriant, mara_varriant, weapon]
    else:
        weapon_list = [kuva_varriant, prime_varriant, tenet_varriant, prisma_varriant, wraith_varriant, synoid_varriant, vandal_varriant, mk1_varriant, sancti_varriant, carmine_varriant, telos_varriant, rakta_varriant, secura_varriant, vaykor_varriant, mara_varriant, weapon]
    #checks if its a varriant, if it is it grabs the grades
    return get_grade(weapon_list, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat)
#return grades with rm translate
def get_varriants_rm(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat):
    (stats, dispo) = get_stats(weapon)
    stat1name = translator_search.translates_rm(stat1name)
    stat2name = translator_search.translates_rm(stat2name)
    stat3name = translator_search.translates_rm(stat3name)
    negstat = translator_search.translates_rm(negstat)
    return grade_weapon(stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat,stats, dispo)

#return grades
def get_grade_varriants(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat):
    (stats, dispo) = get_stats(weapon)
    return grade_weapon(stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat,stats, dispo)

#check if weapon is real and returns dispo and base stats
def is_weapon_in(weapon):
    weapon = str(weapon).title()
    if (weapon in pistol_dispos):
        return True
    elif (weapon in rifle_dispos):
        return True
    elif (weapon in shotgun_dispos):
        return True
    elif (weapon in melee_dispos):
        return True
    elif (weapon in archgun_dispos):
        return True
    else:
        return False

#returns dispo and base stats for weapon
def get_stats(weapon):
    weapon = str(weapon).title()
    if (weapon in pistol_dispos):
        return (pistol_base,pistol_dispos[weapon])
    elif (weapon in rifle_dispos):
        return (rifle_base,rifle_dispos[weapon])
    elif (weapon in shotgun_dispos):
        return (shotgun_base,shotgun_dispos[weapon])
    elif (weapon in melee_dispos):
        return (melee_base,melee_dispos[weapon])
    elif (weapon in archgun_dispos):
        return (archgun_base,archgun_dispos[weapon])
    else:
        raise Exception("weapon type not found",weapon)

#return neg grade
def neg_grade_output(grade):
    if grade > 0:
        grade_send = -abs(grade)
    elif grade < 0:
        grade_send = abs(grade)
    if grade == 0:
        grade_send = grade
    #output grade
    if grade <= -11.1:
        return (":yellow_circle:",grade_send, "? grade")
    if -9.5 >= grade and grade >= -11:
        return (":green_circle:",grade_send, "S grade")
    if -7.5 >= grade and grade > -9.5:
        return (":green_circle:",grade_send, "A+ grade")
    if -5.5 >= grade and grade > -7.5:
        return (":green_circle:",grade_send, "A grade")
    if -3.5 >= grade and grade > -5.5:
        return (":green_circle:",grade_send, "A- grade")
    if -1.5 >= grade and grade > -3.5:
        return (":orange_circle:",grade_send, "B+ grade")
    if 1.5 >= grade and grade > -1.5:
        return (":orange_circle:",grade_send, "B grade")
    if 3.5 >= grade and grade > 1.5:
        return (":orange_circle:",grade_send, "B- grade")
    if 5.5 >= grade and grade > 3.5:
        return (":orange_circle:",grade_send, "C+ grade")
    if 7.5 >= grade and grade > 5.5:
        return (":orange_circle:",grade_send, "C grade")
    if 9.5 >= grade and grade > 7.5:
        return (":red_circle:",grade_send, "C- grade")
    if 11 >= grade and grade > 9.5:
        return (":red_circle:",grade_send, "F grade")
    if grade <= 11.1:
        return (":yellow_circle:",grade_send, "? grade")

#return pos grade
def pos_grade_output(grade):
    #output grade
    if grade >= 11.1:
        return (":yellow_circle:",grade, "? grade")
    if 9.5 <= grade and grade < 11:
        return (":green_circle:",grade, "S grade")
    if 7.5 <= grade and grade < 9.5:
        return (":green_circle:",grade, "A+ grade")
    if 5.5 <= grade and grade < 7.5:
        return (":green_circle:",grade, "A grade")
    if 3.5 <= grade and grade < 5.5:
        return (":green_circle:",grade, "A- grade")
    if 1.5 <= grade and grade < 3.5:
        return (":orange_circle:",grade, "B+ grade")
    if -1.5 <= grade and grade < 1.5:
        return (":orange_circle:",grade, "B grade")
    if -3.5 <= grade and grade < -1.5:
        return (":orange_circle:",grade, "B- grade")
    if -5.5 <= grade and grade < -3.5:
        return (":orange_circle:",grade, "C+ grade")
    if -7.5 <= grade and grade < -5.5:
        return (":orange_circle:",grade, "C grade")
    if -9.5 <= grade and grade < -7.5:
        return (":red_circle:",grade, "C- grade")
    if -11 <= grade and grade < -9.5:
        return (":red_circle:",grade, "F grade")
    if grade <= -11.1:
        return (":yellow_circle:",grade, "? grade")

def riven_math_pos(stat_name, stat_value, stats, dispo, riven_multi):
    if stat_name in stats:
        base_stat = float(stats[stat_name])
        avg_val = round(base_stat * dispo * riven_multi,1)
        grade = round((float(stat_value)-avg_val)*100/avg_val,3)
        #output grade
        return(pos_grade_output(grade))
    
def riven_math_neg(stat_name, stat_value, stats, dispo, riven_multi):
    if stat_name in stats:
        base_stat = float(stats[stat_name])
        avg_val = round(base_stat * dispo * riven_multi,1)
        grade = round((float(stat_value)-avg_val)*100/avg_val,3)
        #output grade
        return(neg_grade_output(grade))

#return neg grade of a +2-1 riven
def grade_neg_2stat(stat_name, stat_value, stats, dispo):
    return riven_math_neg(stat_name, stat_value, stats, dispo, 0.495)

#return neg grade of a +3-1 riven
def grade_neg_3stat(stat_name, stat_value, stats, dispo):
    return riven_math_neg(stat_name, stat_value, stats, dispo, 0.75)

#return pos grade of a +2-1 riven
def grade_2stat_neg(stat_name, stat_value, stats, dispo):
    return riven_math_pos(stat_name, stat_value, stats, dispo, 1.2375)

#return pos grade of a +2-0
def grade_2stat_no_neg(stat_name, stat_value, stats, dispo):
    return riven_math_pos(stat_name, stat_value, stats, dispo, 0.99)

#return pos grade of a +3-0
def grade_3stat_no_neg(stat_name, stat_value, stats, dispo):
    return riven_math_pos(stat_name, stat_value, stats, dispo, 0.75)

#return pos grade of a +3-1
def grade_3stat_neg(stat_name, stat_value, stats, dispo):
    return riven_math_pos(stat_name, stat_value, stats, dispo, 0.9375)

#return all the grades, also checks which version of a riven(+3-1, +3-0, +2-1, +2-0)
def grade_weapon(stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat,stats, dispo):
    grade1 = ""
    grade2 = ""
    grade3 = ""
    grade4 = ""
    if negstat == '[]':
        if stat3name == '[]':
            grade1 = grade_2stat_no_neg(stat1name, stat1val,stats, dispo)
            grade2 = grade_2stat_no_neg(stat2name, stat2val,stats, dispo)
            grade3 = ""
            grade4 = ""
        else:
            grade1 = grade_3stat_no_neg(stat1name, stat1val,stats, dispo)
            grade2 = grade_3stat_no_neg(stat2name, stat2val,stats, dispo)
            grade3 = grade_3stat_no_neg(stat3name, stat3val,stats, dispo)
            grade4 = ""
    else:
        if stat3name == '[]':
            grade1 = grade_2stat_neg(stat1name, stat1val,stats, dispo)
            grade2 = grade_2stat_neg(stat2name, stat2val,stats, dispo)
            grade3 = ""
            grade4 = grade_neg_2stat(negstat, abs(float(negval)),stats, dispo)
        else:
            grade1 = grade_3stat_neg(stat1name, stat1val,stats, dispo)
            grade2 = grade_3stat_neg(stat2name, stat2val,stats, dispo)
            grade3 = grade_3stat_neg(stat3name, stat3val,stats, dispo)
            grade4 = grade_neg_3stat(negstat, abs(float(negval)),stats, dispo)

    return [
        grade1,
        grade2,
        grade3,
        grade4
    ]