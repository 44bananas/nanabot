#bane_patch

banes = ["corpus","grineer","infested"]

def front_to_back(stat, stat_val):
    if any(name in stat.lower() for name in banes):
        stat_val = float(stat_val) * 100 - 100
        stat_val = abs(round(stat_val, 3))
    return stat_val

def back_to_front(stat, stat_val):
    if any(name in stat.lower() for name in banes):
        stat_val = float(stat_val) / 100.0 + 1
        stat_val = abs(round(stat_val, 3))
    return stat_val