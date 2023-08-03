# nanabot
warframe snipe bot for wfm rm and a rough version of tc ocr

commands.py is for the /commands

scraper.py is for the wfm/rm web scraping

tc_ocr_scraper.py is the tc scraper

commands avaiable:
/search -> lets ya search the db of rivens my bot has seen
/blacklist -> add people to the blacklist
/filterlist -> print all the filters in discord
/filterremove -> remove a filter
/teshin -> prints in discord what his weekly rotating item is
/sortie -> prints in discord the sortie missions + debuffs
/events -> tells you the current events and when they end
/arby -> tells you the current arby 
/filters -> add a filter
/searchwfm -> searches current listings on warframe.market
/dispo -> show dispo + what rolls ips
/baro -> show when baro is coming/leaving and his inventory with prices
/rolls -> show the rolls for a weapon
/img_gen -> create a graded img of a riven
/wfm_grade -> given a wfm url grade a riven

libraries used:

python 3.11
discord.py 2.4
sqlite 3
requests
python-dateutil
python-dotenv
pillow
beatufulsoup4
asyncio
grequests
regex
time
json
logging
typing
random
io
pytesseract
