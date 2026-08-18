from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
import re

# Register your models here.
from soccer.models import (
    Comment,
    League,
    Team,
    Area,
    Country,
    Player,
    LikeIpAddress,
    Manager,
    ManagerComment,
    ManagerLikeIpAddress,
    ClubComment,
    ClubCommentLikeIpAddress,
    NationalComment,
    NationalCommentLikeIpAddress,
    Contact,
    ManagerUpdateRequest,
    PlayerUpdateRequest,
    ClubUpdateRequest,
    NationalUpdateRequest,
    ManagerNewCreateRequest,
    PlayerNewCreateRequest,
    ClubNewCreateRequest,
    NationalNewCreateRequest,
    CustomUser,
    Connection,
)

# from user.models import User
from soccer.views import views


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'created_at', 'league', 'team', 'country')
    list_filter = ('league','area')
    search_fields = ['name']


class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'timestamp')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league')
    list_filter = ['league']
    search_fields = ['name']


class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'timestamp')


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'area')
    list_filter = ['area']
    search_fields = ['name']


class CommentAdmin(admin.ModelAdmin):
    list_display = ('player', 'timestamp', 'text')


class ManagerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'created_at', 'league', 'team', 'country')
    list_filter = ('league','area')
    search_fields = ['name']


class ManagerCommentAdmin(admin.ModelAdmin):
    list_display = ('manager', 'timestamp', 'text')


class ClubTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'created_at', 'league')
    list_filter = ['league']
    search_fields = ['name']


class ClubTeamLeagueAdmin(admin.ModelAdmin):
    list_display = ['name']


class ClubTeamCommentAdmin(admin.ModelAdmin):
    list_display = ('team', 'timestamp', 'text')


class NationalTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'created_at', 'area')
    list_filter = ['area']
    search_fields = ['name']


class NationalTeamAreaAdmin(admin.ModelAdmin):
    list_display = ['name']


class NationalTeamCommentAdmin(admin.ModelAdmin):
    list_display = ('country', 'timestamp', 'text')


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'inquiry_details')


class ManagerUpdateRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

    @admin.action(description='監督プロフィール更新')
    def manager_update(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            manager_update_request = get_object_or_404(ManagerUpdateRequest, id = id)
            manager = get_object_or_404(Manager, id = manager_update_request.manager_id)
            manager.league = manager_update_request.league
            manager.team = manager_update_request.team
            manager.area = manager_update_request.area
            manager.country = manager_update_request.country
            manager.name = manager_update_request.name
            manager.birthday = manager_update_request.birthday
            manager.save()
            manager_update_request.delete()
    
    actions = [manager_update]


class PlayerUpdateRequestAdmin(admin.ModelAdmin):
    # change_form_template = 'admin/soccer/approval_refusal_btn.html'
    list_display = ('id', 'name', 'created_at')

    @admin.action(description='選手プロフィール更新')
    def player_update(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            player_update_request = get_object_or_404(PlayerUpdateRequest, id = id)
            player = get_object_or_404(Player, id = player_update_request.player_id)
            player.league = player_update_request.league
            player.team = player_update_request.team
            player.area = player_update_request.area
            player.country = player_update_request.country
            player.name = player_update_request.name
            player.birthday = player_update_request.birthday
            player.height = player_update_request.height
            player.foot = player_update_request.foot
            player.main_position = player_update_request.main_position
            player.second_position = player_update_request.second_position
            player.third_position = player_update_request.third_position
            player.save()
            player_update_request.delete()
    
    actions = [player_update]

class ClubUpdateRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

    @admin.action(description='クラブチームプロフィール更新')
    def club_team_update(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            club_team_update_request = get_object_or_404(ClubUpdateRequest, id = id)
            club_team = get_object_or_404(Team, id = club_team_update_request.team_id)
            club_team.name = club_team_update_request.name
            club_team.year_established = club_team_update_request.year_established
            club_team.home_town = club_team_update_request.home_town
            club_team.league = club_team_update_request.league
            club_team.save()
            club_team_update_request.delete()
    
    actions = [club_team_update]


class NationalUpdateRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

    @admin.action(description='ナショナルチームプロフィール更新')
    def national_team_update(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            national_team_update_request = get_object_or_404(NationalUpdateRequest, id = id)
            national_team = get_object_or_404(Country, id = national_team_update_request.country_id)
            national_team.name = national_team_update_request.name
            national_team.capital = national_team_update_request.capital
            national_team.area = national_team_update_request.area
            national_team.association = national_team_update_request.association
            national_team.save()
            national_team_update_request.delete()
    
    actions = [national_team_update]


class ManagerNewCreateRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

    @admin.action(description='監督ページ新規追加')
    def manager_new_create(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            manager_new_create_request = get_object_or_404(ManagerNewCreateRequest, id = id)
            new_manager = Manager.objects.create(
                league = manager_new_create_request.league,
                team = manager_new_create_request.team,
                area = manager_new_create_request.area,
                country = manager_new_create_request.country,
                name = manager_new_create_request.name,
                birthday = manager_new_create_request.birthday,
                created_at = timezone.now(),
                updated_at = timezone.now(),
                is_public = True
            )
            ManagerComment.objects.create(
                manager = Manager.objects.get(id = new_manager.id),
                author = manager_new_create_request.author,
                ovr = manager_new_create_request.ovr,
                attack = manager_new_create_request.attack_rating,
                defense = manager_new_create_request.defense_rating,
                achievement = manager_new_create_request.achievement_rating,
                management = manager_new_create_request.management_rating,
                development = manager_new_create_request.development_rating,
                political = manager_new_create_request.political_rating,
                text = manager_new_create_request.comment_text,
                timestamp = timezone.now(),
                user_ip_address = manager_new_create_request.user_ip_address,
                like = 0
            )
            manager_new_create_request.delete()
    
    actions = [manager_new_create]


class PlayerNewCreateRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

    @admin.action(description='選手ページ新規追加')
    def player_new_create(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            player_new_create_request = get_object_or_404(PlayerNewCreateRequest, id = id)
            new_player = Player.objects.create(
                league = player_new_create_request.league,
                team = player_new_create_request.team,
                area = player_new_create_request.area,
                country = player_new_create_request.country,
                name = player_new_create_request.name,
                birthday = player_new_create_request.birthday,
                height = player_new_create_request.height,
                foot = player_new_create_request.foot,
                main_position = player_new_create_request.main_position,
                second_position = player_new_create_request.second_position,
                third_position = player_new_create_request.third_position,
                created_at = timezone.now(),
                updated_at = timezone.now(),
                published_at = timezone.now(),
                is_public = True
            )
            Comment.objects.create(
                player = Player.objects.get(id = new_player.id),
                author = player_new_create_request.author,
                ovr = player_new_create_request.ovr,
                shoot = player_new_create_request.shoot_rating,
                dribble = player_new_create_request.dribble_rating,
                pas = player_new_create_request.pass_rating,
                defense = player_new_create_request.defense_rating,
                physical = player_new_create_request.physical_rating,
                speed = player_new_create_request.speed_rating,
                text = player_new_create_request.comment_text,
                timestamp = timezone.now(),
                user_ip_address = player_new_create_request.user_ip_address,
                like = 0
            )
            player_new_create_request.delete()
    
    actions = [player_new_create]


class ClubNewCreateRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

    @admin.action(description='クラブチームページ新規追加')
    def club_team_new_create(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            club_team_new_create_request = get_object_or_404(ClubNewCreateRequest, id = id)
            new_club_team = Team.objects.create(
                name = club_team_new_create_request.name,
                slug = club_team_new_create_request.slug,
                year_established = club_team_new_create_request.year_established,
                home_town = club_team_new_create_request.home_town,
                league = club_team_new_create_request.league,
                image = club_team_new_create_request.image,
                updated_at = timezone.now(),
                created_at = timezone.now(),
                is_public = True
            )
            ClubComment.objects.create(
                team = Team.objects.get(id = new_club_team.id),
                author = club_team_new_create_request.author,
                ovr = club_team_new_create_request.ovr,
                attack = club_team_new_create_request.attack_rating,
                defense = club_team_new_create_request.defense_rating,
                manager = club_team_new_create_request.manager_rating,
                front = club_team_new_create_request.front_rating,
                development = club_team_new_create_request.development_rating,
                text = club_team_new_create_request.comment_text,
                timestamp = timezone.now(),
                user_ip_address = club_team_new_create_request.user_ip_address,
                like = 0
            )
            club_team_new_create_request.delete()
    
    actions = [club_team_new_create]


class ClubNewCreateRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

    @admin.action(description='クラブチームページ新規追加')
    def club_team_new_create(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            club_team_new_create_request = get_object_or_404(ClubNewCreateRequest, id = id)
            new_club_team = Team.objects.create(
                name = club_team_new_create_request.name,
                slug = club_team_new_create_request.slug,
                year_established = club_team_new_create_request.year_established,
                home_town = club_team_new_create_request.home_town,
                league = club_team_new_create_request.league,
                image = club_team_new_create_request.image,
                updated_at = timezone.now(),
                created_at = timezone.now(),
                is_public = True
            )
            ClubComment.objects.create(
                team = Team.objects.get(id = new_club_team.id),
                author = club_team_new_create_request.author,
                ovr = club_team_new_create_request.ovr,
                attack = club_team_new_create_request.attack_rating,
                defense = club_team_new_create_request.defense_rating,
                manager = club_team_new_create_request.manager_rating,
                front = club_team_new_create_request.front_rating,
                development = club_team_new_create_request.development_rating,
                text = club_team_new_create_request.comment_text,
                timestamp = timezone.now(),
                user_ip_address = club_team_new_create_request.user_ip_address,
                like = 0
            )
            club_team_new_create_request.delete()
    
    actions = [club_team_new_create]


class NationalNewCreateRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

    @admin.action(description='代表チームページ新規追加')
    def national_team_new_create(self, request, queryset):
        for title in queryset:
            id = re.sub(r'[^0-9]', '', str(title))
            national_team_new_create_request = get_object_or_404(NationalNewCreateRequest, id = id)
            new_national_team = Country.objects.create(
                name = national_team_new_create_request.name,
                slug = national_team_new_create_request.slug,
                flag = national_team_new_create_request.flag,
                capital = national_team_new_create_request.capital,
                area = national_team_new_create_request.area,
                association = national_team_new_create_request.association,
                updated_at = timezone.now(),
                created_at = timezone.now(),
                is_public = True
            )
            NationalComment.objects.create(
                country = Country.objects.get(id = new_national_team.id),
                author = national_team_new_create_request.author,
                ovr = national_team_new_create_request.ovr,
                attack = national_team_new_create_request.attack_rating,
                defense = national_team_new_create_request.defense_rating,
                manager = national_team_new_create_request.manager_rating,
                association = national_team_new_create_request.association_rating,
                development = national_team_new_create_request.development_rating,
                text = national_team_new_create_request.comment_text,
                timestamp = timezone.now(),
                user_ip_address = national_team_new_create_request.user_ip_address,
                like = 0
            )
            national_team_new_create_request.delete()
    
    actions = [national_team_new_create]


admin.site.register(League, LeagueAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(LikeIpAddress)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(ManagerComment, ManagerCommentAdmin)
admin.site.register(ManagerLikeIpAddress)
admin.site.register(ClubComment, ClubTeamCommentAdmin)
admin.site.register(ClubCommentLikeIpAddress)
admin.site.register(NationalComment, NationalTeamCommentAdmin)
admin.site.register(NationalCommentLikeIpAddress)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ManagerUpdateRequest, ManagerUpdateRequestAdmin)
admin.site.register(PlayerUpdateRequest, PlayerUpdateRequestAdmin)
admin.site.register(ClubUpdateRequest, ClubUpdateRequestAdmin)
admin.site.register(NationalUpdateRequest, NationalUpdateRequestAdmin)
admin.site.register(ManagerNewCreateRequest, ManagerNewCreateRequestAdmin)
admin.site.register(PlayerNewCreateRequest, PlayerNewCreateRequestAdmin)
admin.site.register(ClubNewCreateRequest, ClubNewCreateRequestAdmin)
admin.site.register(NationalNewCreateRequest, NationalNewCreateRequestAdmin)

admin.site.register(CustomUser)
admin.site.register(Connection)