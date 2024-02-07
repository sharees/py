from coroweb import get,post
import logging

@get('/site')
def site():
    logging.info('site...')
    return 'site'