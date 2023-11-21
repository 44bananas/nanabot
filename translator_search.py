#translator_search

#dictionary taking shorthand stat names and full backend stat names
translates = {
    "dmg":"base damage / melee damage",
    "cc":"critical chance",
    "cd":"critical damage",
    "as":"fire rate / attack speed",
    "fr":"fire rate / attack speed",
    "ic":"channeling damage",
    "rec":"recoil",
    "ms":"multishot",
    "tox":"toxin damage",
    "cold":"cold damage",
    "elec":"electric damage",
    "heat":"heat damage",
    "slide":"critical chance on slide attack",
    "fin":"finisher damage",
    "dtg":"damage vs grineer",
    "dti":"damage vs infested",
    "dtc":"damage vs corpus",
    "ammo":"ammo maximum",
    "imp":"impact damage",
    "punc":"puncture damage",
    "slash":"slash damage",
    "mag":"magazine capacity",
    "pt":"punch through",
    "sc":"status chance",
    "sd":"status duration",
    "eff":"channeling efficiency",
    "rls":"reload speed",
    "pfs":"projectile speed",
    "z":"zoom"
}

translates_rm = {
    "Corpus":"damage vs corpus",
    "Grineer":"damage vs grineer",
    "Infested":"damage vs infested",
    "Damage":"base damage / melee damage",
    "CritChance":"critical chance",
    "CritDmg":"critical damage",
    "Speed":"fire rate / attack speed",
    "InitC":"channeling damage",
    "Recoil":"recoil",
    "Multi":"multishot",
    "Toxin":"toxin damage",
    "Electric":"electric damage",
    "Cold":"cold damage",
    "Heat":"heat damage",
    "Slide":"critical chance on slide attack",
    "Finisher":"finisher damage",
    "Ammo":"ammo maximum",
    "Impact":"impact damage",
    "Puncture":"puncture damage",
    "Slash":"slash damage",
    "Magazine":"magazine capacity",
    "Punch":"punch through",
    "StatusC":"status chance",
    "StatusD":"status duration",
    "ComboEfficiency":"channeling efficiency",
    "Reload":"reload speed",
    "Flight":"projectile speed",
    "Zoom":"zoom",
    "ComboGainExtra":"chance to gain extra combo count",
    "Combo Duration":"combo duration",
    "ComboGainLost":"chance to gain combo count",
    "Range":"range"
}

translates_wfm_search = {
    "dmg":"base_damage_/_melee_damage",
    "cc":"critical_chance",
    "cd":"critical_damage",
    "as":"fire_rate_/_attack_speed",
    "fr":"fire_rate_/_attack_speed",
    "ic":"channeling_damage",
    "rec":"recoil",
    "ms":"multishot",
    "tox":"toxin_damage",
    "cold":"cold_damage",
    "elec":"electric_damage",
    "heat":"heat_damage",
    "slide":"critical_chance_on_slide_attack",
    "fin":"finisher_damage",
    "dtg":"damage_vs_grineer",
    "dti":"damage_vs_infested",
    "dtc":"damage_vs_corpus",
    "ammo":"ammo_maximum",
    "imp":"impact_damage",
    "punc":"puncture_damage",
    "slash":"slash_damage",
    "mag":"magazine_capacity",
    "pt":"punch_through",
    "sc":"status_chance",
    "sd":"status_duration",
    "eff":"channeling_efficiency",
    "rls":"reload_speed",
    "pfs":"projectile_speed",
    "z":"zoom"
}

riven_img = {
    "impact damage":"Impact",
    "slash damage":"Slash",
    "puncture damage":"Puncture",
    "channeling efficiency":"Heavy Attack Efficiency",
    "channeling damage":"Initial Combo",
    "damage vs corpus":"Damage to Corpus",
    "damage vs infested":"Damage to Infested",
    "damage vs grineer":"Damage to Grineer",
    "recoil":"Weapon Recoil",
    "toxin damage":"Toxin",
    "heat damage":"Heat",
    "cold damage":"Cold",
    "electric damage":"Electric",
    "projectile speed":"Projectile Flight Speed"
}

riven_img_rifle = {
    "fire rate":"Fire Rate (x2 for Bows)"
}

riven_img_melee = {
    "critical chance":"Critical Chance (x2 for Heavy Attacks)"
}

def translate_riven_img_rifle(stat):
    if stat.lower() in riven_img_rifle:
        return riven_img_rifle[stat.lower()]
    else:
        return stat

def translate_riven_img_melee(stat):
    if stat.lower() in riven_img_melee:
        return riven_img_melee[stat.lower()]
    else:
        return stat

def translate_riven_img(stat):
    if stat.lower() in riven_img:
        return riven_img[stat.lower()]
    else:
        return stat.title()

def translate_filter(stat):
    if stat in translates:
        return translates[stat].lower()
    else:
        return stat

def translate_wfm_search(stat):
    if stat in translates_wfm_search:
        stat_name = translates_wfm_search.get(stat).lower()
        return stat_name
    else:
        return str(stat).lower()

def translate_rm(stat):
    if stat in translates_rm:
        stat_name = translates_rm.get(stat).lower()
        return stat_name
    else:
        return stat

def translate(stat):
    if stat in translates:
        stat_name = translates.get(stat).lower()
        return stat_name
    else:
        return str(stat).lower()