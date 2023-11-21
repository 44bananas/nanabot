#grab_rolls

import pandas as pd
import json

#grab the sheet
excel_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQrEc4ZwJ4WL1FXaMaTAgMtqPQpwVMMr5vd6iE3sxFsjeiHPqhF_fl7Dxny_Spp-99XXPxYzwIXkld5/pub?output=xlsx"
#read the sheet
sheets = pd.read_excel(excel_sheet, sheet_name = None)
#split the sheet
primary = sheets['primary']
secondary = sheets['secondary']
melee = sheets['melee']
archgun = sheets['archgun']
robotic = sheets['robotic']
sticks = sheets['stat sticks']
#list of sheets to loop through
list_of_sheets = [primary, secondary, melee, archgun, robotic, sticks]
#dict of rolls
rolls = {}
for sheet in list_of_sheets:
    #check number of rows to loop through
    number_of_rows = len(sheet)
    #create list of header to figure out where data is at in the doc
    header = sheet.columns.values.tolist()
    column_of_info = 0
    for x in header:
        if "WEAPON" in x:
            weapon = column_of_info
        if "POSITIVE STATS:" in x:
            pos_stats = column_of_info
        if "NEGATIVE STATS:" in x:
            neg_stats = column_of_info
        if "Notes:" in x:
            notes = column_of_info
        column_of_info += 1
    #loop through the rows
    for x in range(number_of_rows):
        rolls.update({sheet.iloc[x].iloc[weapon]:{"pos_stats":sheet.iloc[x].iloc[pos_stats], "neg_stats":sheet.iloc[x].iloc[neg_stats], "notes":sheet.iloc[x].iloc[notes]}})
#write it out
with open("rolls.json", "w") as outfile:
    json.dump(rolls, outfile)