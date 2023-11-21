# nanabot
warframe snipe bot for wfm rm and a rough version of tc ocr

--------------------------------------------------------------------------------------------------------------

commands.py is for the /commands

scraper.py is for the wfm/rm web scraping

tc_ocr_scraper.py is the tc scraper

--------------------------------------------------------------------------------------------------------------

lines to replace in .env:

put your snipe channel id here

put your blacklist channel id here

put your discord bot token here

put your guild id here

put your alerts channel id here

put your sss grade channel id here

put your fff grade channel id here

--------------------------------------------------------------------------------------------------------------

commands available:

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

/top -> shows top 10 most expensive riven sales

/popular -> shows top 10 most popular weapon rivens sold

/veiledprices -> shows veiled riven prices from the last week

/price -> show weekly sell prices(max max avg) of specific riven

--------------------------------------------------------------------------------------------------------------

libraries used:

pandas
python3.11
discord.py2.4
dateutil
sqlite3
requests
os
grequests
typing
random
io
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
