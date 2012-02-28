from util import hook
from mygengo import MyGengo

gengo = MyGengo(
    public_key = 'PlwtF1CZ2tu27IdX_SXNxTFmfN0j|_-pJ^Rf({O-oLl--r^QM4FygRdt^jusSSDE',
    private_key = 'wlXpL=SU[#JpPu[dQaf$v{S3@rg[=95$$TA(k$sb3_6~B_zDKkTbd4#hXxaorIae',
    sandbox = False, # possibly False, depending on your dev needs
)
translation = gengo.postTranslationJob(job = {
    'type': 'text', # REQUIRED. Type to translate, you'll probably always put 'text' here (for now ;)
    'slug': 'Translating English to Japanese with the myGengo API', # REQUIRED. For storing on the myGengo side
    'body_src': 'I love this music!', # REQUIRED. The text you're translating. ;P
    'lc_src': 'en', # REQUIRED. source_language_code (see getServiceLanguages() for a list of codes)  
    'lc_tgt': 'ja', # REQUIRED. target_language_code (see getServiceLanguages() for a list of codes)
    'tier': 'machine', # REQUIRED. tier type ("machine", "standard", "pro", or "ultra")
})

print translation['response']['job']['body_tgt']