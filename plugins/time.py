# Plugin by Lukeroge with some code from Phenny
# <lukeroge@gmail.com> <http://www.dempltr.com/>

from util import hook
from util import http
import re
import time
import locale
import datetime
from BeautifulSoup import BeautifulSoup

TimeZones = {'KST': 9, 'CADT': 10.5, 'EETDST': 3, 'MESZ': 2, 'WADT': 9,
             'EET': 2, 'MST':-7, 'WAST': 8, 'IST': 5.5, 'B': 2,
             'MSK': 3, 'X':-11, 'MSD': 4, 'CETDST': 2, 'AST':-4,
             'HKT': 8, 'JST': 9, 'CAST': 9.5, 'CET': 1, 'CEST': 2,
             'EEST': 3, 'EAST': 10, 'METDST': 2, 'MDT':-6, 'A': 1,
             'UTC': 0, 'ADT':-3, 'EST':-5, 'E': 5, 'D': 4, 'G': 7,
             'F': 6, 'I': 9, 'H': 8, 'K': 10, 'PDT':-7, 'M': 12,
             'L': 11, 'O':-2, 'MEST': 2, 'Q':-4, 'P':-3, 'S':-6,
             'R':-5, 'U':-8, 'T':-7, 'W':-10, 'WET': 0, 'Y':-12,
             'CST':-6, 'EADT': 11, 'Z': 0, 'GMT': 0, 'WETDST': 1,
             'C': 3, 'WEST': 1, 'CDT':-5, 'MET': 1, 'N':-1, 'V':-9,
             'EDT':-4, 'UT': 0, 'PST':-8, 'MEZ': 1, 'BST': 1,
             'ACS': 9.5, 'ATL':-4, 'ALA':-9, 'HAW':-10, 'AKDT':-8,
             'AKST':-9,
             'BDST': 2}

TZ1 = {
 'NDT':-2.5,
 'BRST':-2,
 'ADT':-3,
 'EDT':-4,
 'CDT':-5,
 'MDT':-6,
 'PDT':-7,
 'YDT':-8,
 'HDT':-9,
 'BST': 1,
 'MEST': 2,
 'SST': 2,
 'FST': 2,
 'CEST': 2,
 'EEST': 3,
 'WADT': 8,
 'KDT': 10,
 'EADT': 13,
 'NZD': 13,
 'NZDT': 13,
 'GMT': 0,
 'UT': 0,
 'UTC': 0,
 'WET': 0,
 'WAT':-1,
 'AT':-2,
 'FNT':-2,
 'BRT':-3,
 'MNT':-4,
 'EWT':-4,
 'AST':-4,
 'EST':-5,
 'ACT':-5,
 'CST':-6,
 'MST':-7,
 'PST':-8,
 'YST':-9,
 'HST':-10,
 'CAT':-10,
 'AHST':-10,
 'NT':-11,
 'IDLW':-12,
 'CET': 1,
 'MEZ': 1,
 'ECT': 1,
 'MET': 1,
 'MEWT': 1,
 'SWT': 1,
 'SET': 1,
 'FWT': 1,
 'EET': 2,
 'UKR': 2,
 'BT': 3,
 'ZP4': 4,
 'ZP5': 5,
 'ZP6': 6,
 'WST': 8,
 'HKT': 8,
 'CCT': 8,
 'JST': 9,
 'KST': 9,
 'EAST': 10,
 'GST': 10,
 'NZT': 12,
 'NZST': 12,
 'IDLE': 12
}

TZ2 = {
 'ACDT': 10.5,
 'ACST': 9.5,
 'ADT': 3,
 'AEDT': 11, # hmm
 'AEST': 10, # hmm
 'AHDT': 9,
 'AHST': 10,
 'AST': 4,
 'AT': 2,
 'AWDT':-9,
 'AWST':-8,
 'BAT':-3,
 'BDST':-2,
 'BET': 11,
 'BST':-1,
 'BT':-3,
 'BZT2': 3,
 'CADT':-10.5,
 'CAST':-9.5,
 'CAT': 10,
 'CCT':-8,
 # 'CDT': 5, 
 'CED':-2,
 'CET':-1,
 'CST': 6,
 'EAST':-10,
 # 'EDT': 4, 
 'EED':-3,
 'EET':-2,
 'EEST':-3,
 'EST': 5,
 'FST':-2,
 'FWT':-1,
 'GMT': 0,
 'GST':-10,
 'HDT': 9,
 'HST': 10,
 'IDLE':-12,
 'IDLW': 12,
 # 'IST': -5.5, 
 'IT':-3.5,
 'JST':-9,
 'JT':-7,
 'KST':-9,
 'MDT': 6,
 'MED':-2,
 'MET':-1,
 'MEST':-2,
 'MEWT':-1,
 'MST': 7,
 'MT':-8,
 'NDT': 2.5,
 'NFT': 3.5,
 'NT': 11,
 'NST':-6.5,
 'NZ':-11,
 'NZST':-12,
 'NZDT':-13,
 'NZT':-12,
 'PDT': 7,
 'PST': 8,
 'ROK':-9,
 'SAD':-10,
 'SAST':-9,
 'SAT':-9,
 'SDT':-10,
 'SST':-2,
 'SWT':-1,
 'USZ3':-4,
 'USZ4':-5,
 'USZ5':-6,
 'USZ6':-7,
 'UT': 0,
 'UTC': 0,
 'UZ10':-11,
 'WAT': 1,
 'WET': 0,
 'WST':-8,
 'YDT': 8,
 'YST': 9,
 'ZP4':-4,
 'ZP5':-5,
 'ZP6':-6
}

TZ3 = {
   'AEST': 10,
   'AEDT': 11
}

# TimeZones.update(TZ2) # do these have to be negated?
TimeZones.update(TZ1)
TimeZones.update(TZ3)

r_local = re.compile(r'\([a-z]+_[A-Z]+\)')

def get_time(tz):
   TZ = tz.upper()

   if (TZ == 'UTC') or (TZ == 'Z'):
       msg = time.strftime("\x02%I:%M%p\x02 %A - \x02Time\x02 in \x02 GMT", time.gmtime())
       return msg
   elif r_local.match(tz): # thanks to Mark Shoulsdon (clsn)
       locale.setlocale(locale.LC_TIME, (tz[1:-1], 'UTF-8'))
       msg = time.strftime("\x02%I:%M%p\x02 %A - \x02Time\x02 in \x02" + str(TZ), time.gmtime())
       return msg
   elif TimeZones.has_key(TZ):
       offset = TimeZones[TZ] * 3600
       timenow = time.gmtime(time.time() + offset)
       msg = time.strftime("\x02%I:%M%p\x02 %A - \x02Time\x02 in \x02" + str(TZ), timenow)
       return msg
   #elif tz and tz[0] in ('+', '-') and 4 <= len(tz) <= 6: 
   #    timenow = time.gmtime(time.time() + (int(tz[:3]) * 3600))
   #    msg = time.strftime("4\x02%I:%M%p\x02 %A - \x02Time\x02 in \x02" + str(tz), timenow)
   #    return msg
   else:
       timenow = time.gmtime(time.time() + (int(tz) * 3600))
       msg = time.strftime("\x02%I:%M%p\x02 %A - \x02Time\x02 in\x02 GMT" + str(tz), timenow)
       return msg

@hook.command("time")
def timecommand(inp, say = None):
    ".time <area> -- Gets the time in <area>"

    white_re = re.compile(r'\s+')
    tags_re = re.compile(r'<[^<]*?>')

    page = http.get('http://www.google.com/search', q = "time in " + inp)

    soup = BeautifulSoup(page)

    response = soup.find('td', {'style' : 'font-size:medium'})

    if response:
        output = response.renderContents()

        output = ' '.join(output.splitlines())
        output = output.replace("\xa0", ",")

        output = white_re.sub(' ', output.strip())
        output = tags_re.sub('\x02', output.strip())

        output = output.decode('utf-8', 'ignore')
        return output
    else:
        try:
            output = get_time(inp)
            return output
        except ValueError:
            return "Could not get the time for " + inp + "!"
