from celery import shared_task

@shared_task(queue="celery_queue")
def add(x, y):
    print(x + y)
    return x + y
