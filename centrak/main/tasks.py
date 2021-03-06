import logging
from datetime import datetime
from celery.decorators import task
from dolfin.core import Storage
from . import handlers, sighandlers



@task(name='tasks.import-accounts')
def import_accounts(user_id, filepath):
    # note: user_id is needed in celery's `after_task_publish` signal so
    # collected herein so that it reflects in the body param for the signal
    logging.info('Initiating task: import-accounts')
    ixhandler = handlers.AccountIXHandler()
    ixhandler.import_data(filepath)
    if ixhandler.errors:
        err_message = str(ixhandler.errors)
        logging.error('Import account failed with errors: %s' % err_message)
        raise Exception(err_message)
    logging.info('Import accounts task completed successfully')


@task(name='tasks.import-users')
def import_users(user_id, filepath):
    logging.info('Initiating task: import-users')
    ixhandler = handlers.UserIXHandler({'db': None, 'cache': None})
    ixhandler.import_data(filepath)
    if ixhandler.errors:
        err_message = str(ixhandler.errors)
        logging.error('Import users failed with errors: %s' % err_message)
        raise Exception(err_message)
    logging.info('Import users task completed successfully')


@task(name='tasks.import-offices')
def import_offices(user_id, filepath):
    logging.info('Initializing task: import-offices')
    ixhandler = handlers.OfficeIXHandler({'db': None, 'cache': None})
    ixhandler.import_data(filepath)
    if ixhandler.errors:
        err_message = str(ixhandler.errors)
        logging.error('Import offices failed with errors: %s' % err_message)
        raise Exception(err_message)
    logging.info('Import offices task completed successfully')


@task(name='task.import-station-powerlines')
def import_stations_lines(user_id, filepath):
    logging.info('Initializing task: import-station-powerlines')
    ixhandler = handlers.StationPowerlineIXHandler({'db': None, 'cache': None})
    ixhandler.import_data(filepath)
    if ixhandler.errors:
        err_message = str(ixhandler.errors)
        logging.error('Import stations & powerlines failed with errors: %s' % err_message)
        raise Exception(err_message)
    logging.info('Import stations & powerlines completed successfully')
