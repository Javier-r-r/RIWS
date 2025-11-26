BOT_NAME = 'scraper'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

ROBOTSTXT_OBEY = True

# Keep logging low for demo
LOG_LEVEL = 'INFO'

# Export to JSON
FEEDS = {
    'scuffers_output.json': {
        'format': 'json',
        'encoding': 'utf8',
        'overwrite': True,
    }
}
