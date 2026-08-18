from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from soccer.models import (
    Player,
    Area,
    Country,
    League,
    Team,
    Manager,
)

class StaticViewSitemap(Sitemap):
    """
    メインページのサイトマップ
    """
    changefreq = "daily"
    priority = 0.8
    def items(self):
        return ['soccer:index', 'soccer:player_index', 'soccer:manager_index', 'soccer:club_index', 'soccer:national_index', ]
    def location(self, item):
        return reverse(item)

class StaticViewSitemap(Sitemap):
    """
    静的ページのサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return ['soccer:player_league_list', 'soccer:player_area_list', 'soccer:manager_league_list', 'soccer:manager_area_list', 'soccer:area_item_list', 'soccer:league_item_list',]
    def location(self, item):
        return reverse(item)

class PlayerSitemap(Sitemap):
    """
    【選手】選手のサイトマップ
    """
    changefreq = "never"
    priority = 0.5
    def items(self):
        return Player.objects.filter(is_public=True)
    def location(self, obj):
        return reverse('soccer:player_detail', args=[obj.pk])
    def lastmod(self, obj):
        return obj.published_at

class PlayerLeagueTeamSitemap(Sitemap):
    """
    【選手】リーグ/クラブチームのサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return League.objects.filter()
    def location(self, obj):
        return reverse('soccer:player_league_team', args=[obj.slug])

class TeamPlayerSitemap(Sitemap):
    """
    【選手】クラブチーム/選手のサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return Team.objects.all()
    def location(self, obj):
        return reverse('soccer:team_player_list', args=[obj.slug])

class PlayerAreaCountrySitemap(Sitemap):
    """
    【選手】地域/国籍のサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return Area.objects.all()
    def location(self, obj):
        return reverse('soccer:player_area_country', args=[obj.slug])

class CountryPlayerSitemap(Sitemap):
    """
    【選手】国籍/選手のサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return Country.objects.all()
    def location(self, obj):
        return reverse('soccer:country_player_list', args=[obj.slug])

class ManagerSitemap(Sitemap):
    """
    【監督】監督のサイトマップ
    """
    changefreq = "never"
    priority = 0.5
    def items(self):
        return Manager.objects.filter(is_public=True)
    def location(self, obj):
        return reverse('soccer:manager_detail', args=[obj.pk])
    def lastmod(self, obj):
        return obj.updated_at

class ManagerLeagueTeamSitemap(Sitemap):
    """
    【監督】リーグ/クラブチームのサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return League.objects.filter()
    def location(self, obj):
        return reverse('soccer:manager_league_team', args=[obj.slug])

class TeamManagerSitemap(Sitemap):
    """
    【監督】クラブチーム/監督のサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return Team.objects.all()
    def location(self, obj):
        return reverse('soccer:team_manager_list', args=[obj.slug])

class ManagerAreaCountrySitemap(Sitemap):
    """
    【監督】地域/国籍のサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return Area.objects.all()
    def location(self, obj):
        return reverse('soccer:manager_area_country', args=[obj.slug])

class CountryManagerSitemap(Sitemap):
    """
    【監督】国籍/監督のサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return Country.objects.all()
    def location(self, obj):
        return reverse('soccer:country_manager_list', args=[obj.slug])

class ClubTeamSitemap(Sitemap):
    """
    【クラブ】クラブチームのサイトマップ
    """
    changefreq = "never"
    priority = 0.5
    def items(self):
        return Team.objects.all()
    def location(self, obj):
        return reverse('soccer:club_detail', args=[obj.slug])
    def lastmod(self, obj):
        return obj.updated_at

class LeagueClubSitemap(Sitemap):
    """
    【クラブ】リーグ/クラブチームのサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return League.objects.all()
    def location(self, obj):
        return reverse('soccer:league_club', args=[obj.slug])

class NationalTeamSitemap(Sitemap):
    """
    【代表】代表チームのサイトマップ
    """
    changefreq = "never"
    priority = 0.5
    def items(self):
        return Country.objects.all()
    def location(self, obj):
        return reverse('soccer:national_detail', args=[obj.slug])
    def lastmod(self, obj):
        return obj.updated_at

class AreaNationalSitemap(Sitemap):
    """
    【代表】地域/代表チームのサイトマップ
    """
    changefreq = "daily"
    priority = 0.5
    def items(self):
        return Area.objects.all()
    def location(self, obj):
        return reverse('soccer:area_national', args=[obj.slug])
