import re

from util import hook, http


@hook.command
def mtg(inp):
    ".mtg <name> -- Gets information about Magic the Gathering card <name>."

    url = 'http://magiccards.info/query?v=card&s=cname'
    h = http.get_html(url, q=inp)

    name = h.find('body/table/tr/td/span/a')
    if name is None:
        return "No cards found :("
    card = name.getparent().getparent().getparent()

    type = card.find('td/p').text.replace('\n', '')

    # this is ugly
    text = http.html.tostring(card.xpath("//p[@class='ctext']/b")[0])
    text = text.replace('<br>', '$')
    text = http.html.fromstring(text).text_content()
    text = re.sub(r'(\w+\s*)\$+(\s*\w+)', r'\1. \2', text)
    text = text.replace('$', ' ')
    text = re.sub(r'\(.*?\)', '', text)  # strip parenthetical explanations
    text = re.sub(r'\.(\S)', r'. \1', text)  # fix spacing

    printings = card.find('td/small').text_content()
    printings = re.search(r'Editions:(.*)Languages:', printings).group(1)
    printings = re.findall(r'\s*(.+?(?: \([^)]+\))*) \((.*?)\)',
                           ' '.join(printings.split()))

    printing_out = ', '.join('%s (%s)' % (set_abbrevs.get(x[0], x[0]),
                                          rarity_abbrevs.get(x[1], x[1]))
                                          for x in printings)

    name.make_links_absolute(base_url=url)
    link = name.attrib['href']
    name = name.text_content().strip()
    type = type.strip()
    text = ' '.join(text.split())

    return ' | '.join((name, type, text, printing_out, link))


set_abbrevs = {
    '15th Anniversary': '15ANN',
    'APAC Junior Series': 'AJS',
    'Alara Reborn': 'ARB',
    'Alliances': 'AI',
    'Anthologies': 'AT',
    'Antiquities': 'AQ',
    'Apocalypse': 'AP',
    'Arabian Nights': 'AN',
    'Arena League': 'ARENA',
    'Asia Pacific Land Program': 'APAC',
    'Battle Royale': 'BR',
    'Battle Royale Box Set': 'BRB',
    'Beatdown': 'BTD',
    'Beatdown Box Set': 'BTD',
    'Betrayers of Kamigawa': 'BOK',
    'Celebration Cards': 'UQC',
    'Champions of Kamigawa': 'CHK',
    'Champs': 'CP',
    'Chronicles': 'CH',
    'Classic Sixth Edition': '6E',
    'Coldsnap': 'CS',
    'Coldsnap Theme Decks': 'CSTD',
    'Conflux': 'CFX',
    'Core Set - Eighth Edition': '8E',
    'Core Set - Ninth Edition': '9E',
    'Darksteel': 'DS',
    'Deckmasters': 'DM',
    'Dissension': 'DI',
    'Dragon Con': 'DRC',
    'Duel Decks: Divine vs. Demonic': 'DVD',
    'Duel Decks: Elves vs. Goblins': 'EVG',
    'Duel Decks: Garruk vs. Liliana': 'GVL',
    'Duel Decks: Jace vs. Chandra': 'JVC',
    'Eighth Edition': '8ED',
    'Eighth Edition Box Set': '8EB',
    'European Land Program': 'EURO',
    'Eventide': 'EVE',
    'Exodus': 'EX',
    'Fallen Empires': 'FE',
    'Fifth Dawn': '5DN',
    'Fifth Edition': '5E',
    'Fourth Edition': '4E',
    'Friday Night Magic': 'FNMP',
    'From the Vault: Dragons': 'FVD',
    'From the Vault: Exiled': 'FVE',
    'Future Sight': 'FUT',
    'Gateway': 'GRC',
    'Grand Prix': 'GPX',
    'Guildpact': 'GP',
    'Guru': 'GURU',
    'Happy Holidays': 'HHO',
    'Homelands': 'HL',
    'Ice Age': 'IA',
    'Introductory Two-Player Set': 'ITP',
    'Invasion': 'IN',
    'Judge Gift Program': 'JR',
    'Judgment': 'JU',
    'Junior Series': 'JSR',
    'Legend Membership': 'DCILM',
    'Legends': 'LG',
    'Legions': 'LE',
    'Limited Edition (Alpha)': 'LEA',
    'Limited Edition (Beta)': 'LEB',
    'Limited Edition Alpha': 'LEA',
    'Limited Edition Beta': 'LEB',
    'Lorwyn': 'LW',
    'MTGO Masters Edition': 'MED',
    'MTGO Masters Edition II': 'ME2',
    'MTGO Masters Edition III': 'ME3',
    'Magic 2010': 'M10',
    'Magic Game Day Cards': 'MGDC',
    'Magic Player Rewards': 'MPRP',
    'Magic Scholarship Series': 'MSS',
    'Magic: The Gathering Launch Parties': 'MLP',
    'Media Inserts': 'MBP',
    'Mercadian Masques': 'MM',
    'Mirage': 'MR',
    'Mirrodin': 'MI',
    'Morningtide': 'MT',
    'Multiverse Gift Box Cards': 'MGBC',
    'Nemesis': 'NE',
    'Ninth Edition Box Set': '9EB',
    'Odyssey': 'OD',
    'Onslaught': 'ON',
    'Planar Chaos': 'PC',
    'Planechase': 'PCH',
    'Planeshift': 'PS',
    'Portal': 'PO',
    'Portal Demogame': 'POT',
    'Portal Second Age': 'PO2',
    'Portal Three Kingdoms': 'P3K',
    'Premium Deck Series: Slivers': 'PDS',
    'Prerelease Events': 'PTC',
    'Pro Tour': 'PRO',
    'Prophecy': 'PR',
    'Ravnica: City of Guilds': 'RAV',
    'Release Events': 'REP',
    'Revised Edition': 'RV',
    'Saviors of Kamigawa': 'SOK',
    'Scourge': 'SC',
    'Seventh Edition': '7E',
    'Shadowmoor': 'SHM',
    'Shards of Alara': 'ALA',
    'Starter': 'ST',
    'Starter 1999': 'S99',
    'Starter 2000 Box Set': 'ST2K',
    'Stronghold': 'SH',
    'Summer of Magic': 'SOM',
    'Super Series': 'SUS',
    'Tempest': 'TP',
    'Tenth Edition': '10E',
    'The Dark': 'DK',
    'Time Spiral': 'TS',
    'Time Spiral Timeshifted': 'TSTS',
    'Torment': 'TR',
    'Two-Headed Giant Tournament': 'THGT',
    'Unglued': 'UG',
    'Unhinged': 'UH',
    'Unhinged Alternate Foils': 'UHAA',
    'Unlimited Edition': 'UN',
    "Urza's Destiny": 'UD',
    "Urza's Legacy": 'UL',
    "Urza's Saga": 'US',
    'Visions': 'VI',
    'Weatherlight': 'WL',
    'Worlds': 'WRL',
    'WotC Online Store': 'WOTC',
    'Zendikar': 'ZEN'}

rarity_abbrevs = {
    'Land': 'L',
    'Common': 'C',
    'Uncommon': 'UC',
    'Rare': 'R',
    'Special': 'S',
    'Mythic Rare': 'MR'}
