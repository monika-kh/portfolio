from django.http import HttpResponseRedirect


def index(request):
    '''
    To redirect app to register page.
    '''
    return HttpResponseRedirect("register/")