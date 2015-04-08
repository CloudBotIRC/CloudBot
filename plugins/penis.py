from cloudbot import hook
import random


dong = ['(_)_)============D~~~~~', '8>', 'B==D', 'B==Q', '8~~~D']

@hook.command(autohelp=False)
def penis(message):
    """much dongs, very ween"""
    message(random.choice(dong))
