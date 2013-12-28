import random
from util import hook, text

@hook.command('mark')
def mark(input):
    """mark -- Spreads the glory of Mark Harmon"""
    responses = [
    "Praise our lord Mark Harmon",
    "Have you considered joining the Church of Mark Harmon?",
    "M A R K H A R M O N",
    "Did you know, Mark Harmon used to be a lifeguard?",
    "Mark Harmon is our guide in these dark times.",
    "Why not donate to the Church of Mark Harmon and help further our cause?",
    "MERK HERMERN",
    "Mark Harmon can cut through a hot knife with butter.",
    "Mark Harmon can win a game of connect four in only three moves."
    "PRAISE MARK HARMON",
    "GLORY TO OUR LORD",
    "Become a Mark Harmoner today and promote Mark Harmony!",
    "The Church of Mark Harmon choir can achieve perfect Mark Harmony."
    "Mark!"
    ]

    return random.choice(responses)
