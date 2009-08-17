from django.db.models.signals import pre_save
import threading
import datetime

stash = threading.local()

def get_current_user():
    """Get the user whose session resulted in the current code running. (Only valid during requests.)"""
    return stash.current_user

def set_current_user(user):
    stash.current_user = user

set_current_user(None)

def onanymodel_presave(sender, **kwargs):
    current_user = stash.current_user
    if current_user is None or not current_user.is_authenticated():
        # if there is no current user or we're an unauthenticated user (ie: guest)
        # then don't do anything. The save() will fail if created_by or modified_by
        # are null=False, and not otherwise; ie the behaviour is controlled by the
        # models, as desired.
        current_user = None

    obj = kwargs['instance']
    if hasattr(obj, 'modified_at'):
        obj.modified_at = datetime.datetime.now()
    if hasattr(obj, 'modified_by_id'):
        obj.modified_by = current_user
    if not obj.pk:
        if hasattr(obj, 'created_at'):
            obj.created_at = datetime.datetime.now()
        if hasattr(obj, 'created_by_id'):
            obj.created_by = current_user

pre_save.connect(onanymodel_presave)

class AutoCreatedAndModifiedFields:
    def process_request(self, request):
        set_current_user(request.user)
