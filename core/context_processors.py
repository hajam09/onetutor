def cookieConsentStage(request):
    return {
        'hasCookieAndSessionConsent': request.session.session_key is not None
    }
