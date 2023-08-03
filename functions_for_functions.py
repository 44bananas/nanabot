#functions_for_functions

#returns the value found by key in a nested dict
async def find_by_key(data,target):
    return [val[target] for key, val in data.items() if target in val]

#replace text before sending to channels
async def print_replace(data):
    data = data.replace("channeling efficiency","heavy attack efficiency")
    data = data.replace("channeling damage", "intial combo")
    return data