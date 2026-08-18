"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('soccer/', include('soccer.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap

app_name = 'soccer'
admin.site.site_title = '管理サイト' 
admin.site.site_header = 'みんなのサッカーラボ管理サイト' 
admin.site.index_title = 'メニュー'

from .sitemaps import (
    ManagerSitemap,
    PlayerSitemap,
    StaticViewSitemap,
    PlayerLeagueTeamSitemap,
    TeamPlayerSitemap,
    PlayerAreaCountrySitemap,
    CountryPlayerSitemap,

    ManagerLeagueTeamSitemap,
    TeamManagerSitemap,
    ManagerAreaCountrySitemap,
    CountryManagerSitemap,

    ClubTeamSitemap,
    NationalTeamSitemap,
    LeagueClubSitemap,
    AreaNationalSitemap,
)

sitemaps = {
    'static': StaticViewSitemap,

    'player': PlayerSitemap,
    'player_leagueteam': PlayerLeagueTeamSitemap,
    'team_player':TeamPlayerSitemap,
    'player_area_country': PlayerAreaCountrySitemap,
    'country_player':CountryPlayerSitemap,

    'manager': ManagerSitemap,
    'manager_leagueteam': ManagerLeagueTeamSitemap,
    'team_manager':TeamManagerSitemap,
    'manager_area_country': ManagerAreaCountrySitemap,
    'country_manager':CountryManagerSitemap,

    'club_team': ClubTeamSitemap,
    'national_team': NationalTeamSitemap,
    'league_club': LeagueClubSitemap,
    'area_national': AreaNationalSitemap,
}

urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path('', include('soccer.urls')),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
