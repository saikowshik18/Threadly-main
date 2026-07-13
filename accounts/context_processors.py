def user_profile_context(request):
    """
    Injects the StudentProfile into every template context so templates
    can use {{ user_profile.avatar_url }}, {{ user_profile.campus }} etc.
    Also exposes unread badge counters for the navbar.
    """
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Exception:
            profile = None

        unread_notifications = 0
        unread_messages = 0

        if profile:
            unread_notifications = profile.unread_notifications_count
            unread_messages = profile.unread_messages_count

        return {
            'user_profile': profile,
            'unread_notifications_count': unread_notifications,
            'unread_messages_count': unread_messages,
        }
    return {
        'user_profile': None,
        'unread_notifications_count': 0,
        'unread_messages_count': 0,
    }
