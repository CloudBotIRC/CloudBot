from util import http, hook


@hook.command(autohelp=False)
def bitcoin(inp, say=None):
    ".bitcoin -- gets current exchange rate for bitcoins from mtgox"
    data = http.get_json("https://mtgox.com/code/data/ticker.php")
    ticker = data['ticker']
    say("Current: \x0307$%(buy).2f\x0f - High: \x0307$%(high).2f\x0f"
        " - Low: \x0307$%(low).2f\x0f - Volume: %(vol)s" % ticker)
