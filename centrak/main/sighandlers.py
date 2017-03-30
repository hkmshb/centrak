import logging
from celery.signals import after_task_publish, task_success, task_failure
from core.models import Notification


_TASK_MESSAGES = {
    'tasks.import-accounts': 
        "Accounts import task published on task queue. Import operation " \
        "might take a while, continue with other tasks or await a task " \
        "completion notification.",
    'tasks.import-accounts-success': "Accounts import completed successfully.",
    'tasks.import-accounts-failure': "Accounts import failed with error: %s",
}

@after_task_publish.connect
def task_sent_handler(sender=None, headers=None, body=None, **kwargs):
    if not sender or sender not in _TASK_MESSAGES:
        return
    
    try:
        info = headers if headers and 'task' in headers else body
        task_id, user_id = (info.get('id'), info.get('args')[0])

        # create notification
        Notification.objects.create(user_id=user_id, task_id=task_id, 
            task_status='published', message=_TASK_MESSAGES[sender])
    except Exception as ex:
        message_fmt = "Notification creation for published task '{}' failed " \
                    + "with error: {}"
        logging.error(message_fmt.format(sender, str(ex)))


@task_success.connect
def task_success_handler(sender, result, **kwargs):
    message_key = '%s-success' % sender.name
    info = sender.request
    try:
        task_id, user_id = (info.get('id'), info.get('args')[0])
        Notification.objects.create(user_id=user_id, task_id=task_id,
            task_status='success', message=_TASK_MESSAGES[message_key])
    except Exception as ex:
        message_fmt = "Notification creation for successful task '{}' failed " \
                    + "with error: {}"
        logging.error(message_fmt.format(sender.name, str(ex)))


@task_failure.connect
def task_failure_handler(sender, task_id, exception, args, **kwargs):
    message_key = '%s-failure' % sender.name
    try:
        message = _TASK_MESSAGES[message_key] % str(exception)
        Notification.objects.create(user_id=args[0], task_id=task_id, 
            task_status='failure', message=message)
    except Exception as ex:
        message_fmt = "Notification creation for task '{}' which failed with " \
                    + "error:\n{}\nfailed with: {}"
        logging.error(message_fmt.format(sender.name, str(exception), str(ex)))
