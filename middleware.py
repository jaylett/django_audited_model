# Copyright (c) 2009 James Aylett <http://tartarus.org/james/computers/django/>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from django.db.models.signals import pre_save
import threading
import datetime

stash = threading.local()

def get_current_user():
    """Get the user whose session resulted in the current code running. (Only valid during requests.)"""
    return getattr(stash, 'current_user', None)

def set_current_user(user):
    stash.current_user = user

def onanymodel_presave(sender, **kwargs):
    current_user = get_current_user()
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
        if current_user and current_user.is_authenticated():
            obj.modified_by = current_user
    if not obj.pk:
        if hasattr(obj, 'created_at'):
            obj.created_at = datetime.datetime.now()
        if hasattr(obj, 'created_by_id') and not obj.created_by:
            obj.created_by = current_user

pre_save.connect(onanymodel_presave)

class AutoCreatedAndModifiedFields:
    def process_request(self, request):
        set_current_user(request.user)
