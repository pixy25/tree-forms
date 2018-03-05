import threading


thread_local = threading.local()
thread_local.history = []
thread_local.current_form = None


def _is_set():
    return thread_local.current_form is not None


def set_current_form(form):
    if _is_set():
        thread_local.history.append(thread_local.current_form)
    thread_local.current_form = form


def rollback_current_form():
    if thread_local.history:
        thread_local.current_form = thread_local.history.pop()
    else:
        thread_local.current_form = None


def current_form():
    if _is_set():
        return thread_local.current_form
    from forms import BaseForm
    return BaseForm({})