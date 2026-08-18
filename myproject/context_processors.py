from django.db.models import Count, Q
from django.conf import settings

from soccer.models import (
    League,
    Team,
    Area,
    Country,
)


def common(request):
    context = {
        'leagues': League.objects.annotate(num_teams=Count('team')),
        'teams': Team.objects.annotate(
            num_players=Count('player', filter=Q(player__is_public=True))),
        'areas': Area.objects.annotate(num_countries=Count('country')),
        'countries': Country.objects.annotate(
            num_players=Count('player', filter=Q(player__is_public=True))),
        'manager_leagues': League.objects.annotate(num_teams=Count('team')),
        'manager_teams': Team.objects.all().annotate(
            num_managers=Count('manager', filter=Q(manager__is_public=True))).order_by('-num_managers'),
        'manager_areas': Area.objects.annotate(num_countries=Count('country')),
        'manager_countries': Country.objects.annotate(
            num_managers=Count('manager', filter=Q(manager__is_public=True))).order_by('-num_managers'),
        'club_leagues': League.objects.annotate(
            num_teams=Count('team', filter=Q(team__is_public=True))),
        'national_areas': Area.objects.annotate(
            num_countries=Count('country', filter=Q(country__is_public=True))),
        'GOOGLE_ADSENSE_PUBLISHER_ID': settings.GOOGLE_ADSENSE_PUBLISHER_ID,
        'GOOGLE_ANALYTICS_TRACKING_ID': settings.GOOGLE_ANALYTICS_TRACKING_ID,
    }
    return context
