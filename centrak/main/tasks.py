import logging
from datetime import datetime
from celery.decorators import task
from . import handlers, sighandlers



@task(name='tasks.import-accounts')
def import_accounts(user_id, filepath):
    # note: user_id is needed in celery's `after_task_publish` signal so
    # collected herein so that it reflects in the body param for the signal
    logging.info('Initiating task: import-accounts')
    ixhandler = handlers.AccountIXHandler(filepath)
    ixhandler.load_from_excel()
    
    message = 'Import accounts task failed with error: %s'
    logging.error(message % str(ex))
