from . import models

def site_settings(request):

    site_settings = models.SiteSettings.get_settings()
    return {'site': site_settings}