from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import messages
from allauth.account.signals import user_logged_out

@receiver(user_logged_in)
def kill_other_sessions(sender, request, user, **kwargs):
    current_session_key = request.session.session_key
    sessions_deleted = False

    # Loop through all sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())

    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):
            if session.session_key != current_session_key:
                # Mark this session as being force-logged-out before deleting
                data['force_logged_out'] = True
                session.session_data = Session.objects.encode(data)
                session.save()
                session.delete()
                sessions_deleted = True

    if sessions_deleted:
        messages.info(request, 'Your other active sessions have been logged out for security.')
