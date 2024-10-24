from scrapers import fusion_solar_scraper, tauron_scraper
from datetime import datetime
from create_excel import create_excel

#put the dates you want to gather data
#datetime(year,month,day)

tauron_start_date = datetime()
tauron_end_date = datetime()
tauron_username = ''
tauron_password = ''

fusion_end_date = datetime()
fusion_login = ''
fusion_password = ''

#data scrap
energy = tauron_scraper(tauron_start_date, tauron_end_date, tauron_username, tauron_password)
saved_yield = fusion_solar_scraper(fusion_end_date, fusion_login, fusion_password)

#put it together to excel

create_excel(energy, saved_yield)