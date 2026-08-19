from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import CreateView

from django.db.models import Count, Avg, Q, F
from django.http import Http404, HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.conf import settings
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib import messages

from datetime import timedelta
from django.utils import timezone

import json,statistics
from django.http.response import JsonResponse

from soccer.forms import(
    CommentForm,
    PlayerUpdateRequestForm,
    PlayerNewCreateRequestForm,
)

from soccer.models import(
    Comment,
    League,
    Team,
    Area,
    Country,
    Player,
    Comment,
    LikeIpAddress,
    PlayerUpdateRequest,
    PlayerNewCreateRequest,
    POSITION_CHOICES,
    DOMINANT_FOOT_CHOICES
)

from soccer.views import views


# 【選手】トップページ
class PlayerIndexView(ListView):
    template_name = 'soccer/player/player_index.html'
    model = Player
    paginate_by = 5

    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super(PlayerIndexView, self).get_context_data(**kwargs)
        context.update({
            'comment_list': Comment.objects.all(),
        })
        return context


# 【選手】詳細（コメント最新順）
class PlayerDetailView(DetailView):
    model = Player
    template_name = 'soccer/player/player_detail.html'
    queryset = Player.objects.annotate(
        num_comments=Count('comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(PlayerDetailView, self).get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        comments = context['player'].comments.all()
        paginator = Paginator(comments, per_page=10)
        context['comments'] = paginator.get_page(page_number)
        return context


# 【選手】詳細（コメントいいね数順）
class PlayerDetailLikeCountView(DetailView):
    model = Player
    template_name = 'soccer/player/player_detail.html'
    queryset = Player.objects.annotate(
        num_comments=Count('comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(PlayerDetailLikeCountView, self).get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        comments = context['player'].comments.all().order_by('-like', '-timestamp')
        paginator = Paginator(comments, per_page=10)
        context['comments'] = paginator.get_page(page_number)
        return context


# 【選手】詳細（コメント高評価順）
class PlayerDetailHighRatingView(DetailView):
    model = Player
    template_name = 'soccer/player/player_detail.html'
    queryset = Player.objects.annotate(
        num_comments=Count('comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(PlayerDetailHighRatingView, self).get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        comments = context['player'].comments.all().order_by('-ovr', '-like', '-timestamp')
        paginator = Paginator(comments, per_page=10)
        context['comments'] = paginator.get_page(page_number)
        return context


# 【選手】詳細（コメント低評価順）
class PlayerDetailLowRatingView(DetailView):
    model = Player
    template_name = 'soccer/player/player_detail.html'
    queryset = Player.objects.annotate(
        num_comments=Count('comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(PlayerDetailLowRatingView, self).get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        comments = context['player'].comments.all().order_by('ovr', '-like', '-timestamp')
        paginator = Paginator(comments, per_page=10)
        context['comments'] = paginator.get_page(page_number)
        return context


# 【選手】リスト（最新順）
class PlayerListView(ListView):
    model = Player
    paginate_by = 10
    template_name = 'soccer/player/player_list.html'
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-created_at')


# 【選手】リスト（コメント数順）
class PlayerListCommentCountView(ListView):
    model = Player
    paginate_by = 10
    template_name = 'soccer/player/player_list.html'
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-num_comments','-created_at')


# 【選手】リスト（平均総合評価順）
class PlayerListAvgRatingView(ListView):
    model = Player
    template_name = 'soccer/player/player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments'), avg_ovr=Avg('comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments','-created_at')


# 【選手】ポジションリスト
class PlayerPositionListView(ListView):
    template_name = 'soccer/player/position_list.html'
    queryset = Player.objects.all()
    
    def get_context_data(self):
        context = {}
        for position in POSITION_CHOICES:
            num_player = Player.objects.filter(main_position=position[0]).count()
            context[f'num_{position[0].lower()}'] = num_player
        return context


# 【選手】リーグリスト
class PlayerLeagueListView(ListView):
    template_name = 'soccer/player/league_list.html'
    queryset = League.objects.annotate(
        num_teams=Count('team'))


# 【選手】地域リスト
class PlayerAreaListView(ListView):
    template_name = 'soccer/player/area_list.html'
    queryset = Area.objects.annotate(
        num_countries=Count('country'))


# 【選手】リーグごとのチームリスト
class PlayerLeagueTeamView(ListView):
    model = Team
    template_name = 'soccer/player/league_team.html'
    queryset = Team.objects.annotate(
        num_players=Count('player')).order_by('-num_players', 'name')

    def get_queryset(self):
        player_league_slug = self.kwargs['player_league_slug']
        self.player_league = get_object_or_404(League, slug=player_league_slug)
        qs = super().get_queryset().filter(league=self.player_league)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league'] = self.player_league
        return context


# 【選手】チームごとの選手リスト（最新順）
class TeamPlayerListView(ListView):
    model = Player
    template_name = 'soccer/player/team_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-created_at')

    def get_queryset(self):
        player_team_slug = self.kwargs['player_team_slug']
        self.player_team = get_object_or_404(Team, slug=player_team_slug)
        qs = super().get_queryset().filter(team=self.player_team)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.player_team
        return context


# 【選手】チームごとの選手リスト（コメント数順）
class TeamPlayerListCommentCountView(ListView):
    model = Player
    template_name = 'soccer/player/team_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-num_comments','-created_at')

    def get_queryset(self):
        player_team_slug = self.kwargs['player_team_slug']
        self.player_team = get_object_or_404(Team, slug=player_team_slug)
        qs = super().get_queryset().filter(team=self.player_team)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.player_team
        return context


# 【選手】チームごとの選手リスト（平均総合評価順）
class TeamPlayerListAvgRatingView(ListView):
    model = Player
    template_name = 'soccer/player/team_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments'), avg_ovr=Avg('comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')

    def get_queryset(self):
        player_team_slug = self.kwargs['player_team_slug']
        self.player_team = get_object_or_404(Team, slug=player_team_slug)
        qs = super().get_queryset().filter(team=self.player_team)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.player_team
        return context


# 【選手】チームごとのポジションリスト
class TeamPositionListView(ListView):
    template_name = 'soccer/player/team_position_list.html'
    queryset = Player.objects.all()
    
    def get_queryset(self):
        player_team_slug = self.kwargs['player_team_slug']
        self.player_team = get_object_or_404(Team, slug=player_team_slug)
        qs = super().get_queryset().filter(team=self.player_team)
        return qs

    def get_context_data(self):
        context = {}
        for position in POSITION_CHOICES:
            num_player = Player.objects.filter(main_position=position[0], team=self.player_team).count()
            context[f'num_{position[0].lower()}'] = num_player
        context['team'] = self.player_team
        return context


# 【選手】チームごとのポジション別選手リスト（最新順）
class TeamPlayerListPositionView(ListView):
    model = Player
    template_name = 'soccer/player/team_player_list_position.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-created_at')

    def get_queryset(self):
        player_team_slug = self.kwargs['player_team_slug']
        self.main_position = self.kwargs['position_name']
        self.player_team = get_object_or_404(Team, slug=player_team_slug)
        qs = super().get_queryset().filter(team=self.player_team, main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.player_team
        context['main_position'] = self.main_position
        return context


# 【選手】チームごとのポジション別選手リスト（コメント数順）
class TeamPlayerListPositionCommentCountView(ListView):
    model = Player
    template_name = 'soccer/player/team_player_list_position.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-num_comments','-created_at')

    def get_queryset(self):
        player_team_slug = self.kwargs['player_team_slug']
        self.main_position = self.kwargs['position_name']
        self.player_team = get_object_or_404(Team, slug=player_team_slug)
        qs = super().get_queryset().filter(team=self.player_team, main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.player_team
        context['main_position'] = self.main_position
        return context


# 【選手】チームごとのポジション別選手リスト（平均総合評価順）
class TeamPlayerListPositionAvgRatingView(ListView):
    model = Player
    template_name = 'soccer/player/team_player_list_position.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments'), avg_ovr=Avg('comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')

    def get_queryset(self):
        player_team_slug = self.kwargs['player_team_slug']
        self.main_position = self.kwargs['position_name']
        self.player_team = get_object_or_404(Team, slug=player_team_slug)
        qs = super().get_queryset().filter(team=self.player_team, main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.player_team
        context['main_position'] = self.main_position
        return context


# 【選手】地域ごとの国リスト
class PlayerAreaCountryView(ListView):
    model = Country
    template_name = 'soccer/player/area_country.html'
    queryset = Country.objects.annotate(
        num_players=Count('player')).order_by('-num_players', 'name')

    def get_queryset(self):
        player_area_slug = self.kwargs['player_area_slug']
        self.player_area = get_object_or_404(Area, slug=player_area_slug)
        qs = super().get_queryset().filter(area=self.player_area)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['area'] = self.player_area
        return context
 

# 【選手】国ごとの選手リスト（最新順）
class CountryPlayerListView(ListView):
    model = Player
    template_name = 'soccer/player/country_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-created_at')

    def get_queryset(self):
        player_country_slug = self.kwargs['player_country_slug']
        self.player_country = get_object_or_404(Country, slug=player_country_slug)
        qs = super().get_queryset().filter(country=self.player_country)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.player_country
        return context


# 【選手】国ごとの選手リスト（コメント数順）
class CountryPlayerListCommentCountView(ListView):
    model = Player
    template_name = 'soccer/player/country_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-num_comments','-created_at')

    def get_queryset(self):
        player_country_slug = self.kwargs['player_country_slug']
        self.player_country = get_object_or_404(Country, slug=player_country_slug)
        qs = super().get_queryset().filter(country=self.player_country)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.player_country
        return context


# 【選手】国籍ごとの選手リスト（平均総合評価順）
class CountryPlayerListAvgRatingView(ListView):
    model = Player
    template_name = 'soccer/player/country_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments'), avg_ovr=Avg('comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')

    def get_queryset(self):
        player_country_slug = self.kwargs['player_country_slug']
        self.player_country = get_object_or_404(Country, slug=player_country_slug)
        qs = super().get_queryset().filter(country=self.player_country)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.player_country
        return context


# 【選手】国籍ごとのポジションリスト
class CountryPositionListView(ListView):
    template_name = 'soccer/player/country_position_list.html'
    queryset = Player.objects.all()
    
    def get_queryset(self):
        player_country_slug = self.kwargs['player_country_slug']
        self.player_country = get_object_or_404(Country, slug=player_country_slug)
        qs = super().get_queryset().filter(country=self.player_country)
        return qs

    def get_context_data(self):
        context = {}
        for position in POSITION_CHOICES:
            num_player = Player.objects.filter(main_position=position[0], country=self.player_country).count()
            context[f'num_{position[0].lower()}'] = num_player
        context['country'] = self.player_country
        return context


# 【選手】国籍ごとのポジション別選手リスト（最新順）
class CountryPlayerListPositionView(ListView):
    model = Player
    template_name = 'soccer/player/country_player_list_position.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-created_at')

    def get_queryset(self):
        player_country_slug = self.kwargs['player_country_slug']
        self.main_position = self.kwargs['position_name']
        self.player_country = get_object_or_404(Country, slug=player_country_slug)
        qs = super().get_queryset().filter(country=self.player_country, main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.player_country
        context['main_position'] = self.main_position
        return context


# 【選手】国籍ごとのポジション別選手リスト（コメント数順）
class CountryPlayerListPositionCommentCountView(ListView):
    model = Player
    template_name = 'soccer/player/country_player_list_position.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-num_comments','-created_at')

    def get_queryset(self):
        player_country_slug = self.kwargs['player_country_slug']
        self.main_position = self.kwargs['position_name']
        self.player_country = get_object_or_404(Country, slug=player_country_slug)
        qs = super().get_queryset().filter(country=self.player_country, main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.player_country
        context['main_position'] = self.main_position
        return context


# 【選手】国籍ごとのポジション別選手リスト（平均総合評価順）
class CountryPlayerListPositionAvgRatingView(ListView):
    model = Player
    template_name = 'soccer/player/country_player_list_position.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments'), avg_ovr=Avg('comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')

    def get_queryset(self):
        player_country_slug = self.kwargs['player_country_slug']
        self.main_position = self.kwargs['position_name']
        self.player_country = get_object_or_404(Country, slug=player_country_slug)
        qs = super().get_queryset().filter(country=self.player_country, main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.player_country
        context['main_position'] = self.main_position
        return context


# 【選手】ポジションごとの選手リスト（最新順）
class PositionPlayerListView(ListView):
    model = Player
    template_name = 'soccer/player/position_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-created_at')

    def get_queryset(self):
        self.main_position = self.kwargs['position_name']
        qs = super().get_queryset().filter(main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_position'] = self.main_position
        return context


# 【選手】ポジションごとの選手リスト（コメント数順）
class PositionPlayerListCommentCountView(ListView):
    model = Player
    template_name = 'soccer/player/position_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-num_comments','-created_at')

    def get_queryset(self):
        self.main_position = self.kwargs['position_name']
        qs = super().get_queryset().filter(main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_position'] = self.main_position
        return context


# 【選手】ポジションごとの選手リスト（平均総合評価順）
class PositionPlayerListAvgRatingView(ListView):
    model = Player
    template_name = 'soccer/player/position_player_list.html'
    paginate_by = 10
    queryset = Player.objects.annotate(
        num_comments=Count('comments'), avg_ovr=Avg('comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')

    def get_queryset(self):
        self.main_position = self.kwargs['position_name']
        qs = super().get_queryset().filter(main_position=self.main_position)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_position'] = self.main_position
        return context


# 【選手|管理画面】リーグ別にチームを選択できる
def get_team(request):
    id = request.GET.get('id', '')
    result = list(Team.objects.filter(
        league_id=int(id)).values('id', 'name'))
    return HttpResponse(json.dumps(result), content_type="application/json")


# 【選手|管理画面】地域別に国籍を選択できる
def get_country(request):
    id = request.GET.get('id', '')
    result = list(Country.objects.filter(
        area_id=int(id)).values('id', 'name'))
    return HttpResponse(json.dumps(result), content_type="application/json")


# 【選手】選手の検索機能
class SearchPlayerView(ListView):
    model = Player
    template_name = 'soccer/player/search_player.html'
    paginate_by = 10

    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by( '-num_comments','-created_at')

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        lookups = (
            Q(name__icontains=query) 
        )
        if query is not None:
            qs = super().get_queryset().filter(lookups).distinct()
            return qs
        qs = super().get_queryset()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        return context
        

# 【選手】コメントリスト（最新順）
class CommnetListView(ListView):
    model = Comment
    template_name = 'soccer/player/comment_list.html'
    paginate_by = 10
    queryset = Comment.objects.order_by('-timestamp')


# 【選手】コメントリスト（いいね数順）
class CommnetListLikeCountView(ListView):
    model = Comment
    template_name = 'soccer/player/comment_list.html'
    paginate_by = 10
    queryset = Comment.objects.order_by('-like', '-timestamp')


# 【選手】コメントリスト（高評価順）
class CommnetListHighRatingView(ListView):
    model = Comment
    template_name = 'soccer/player/comment_list.html'
    paginate_by = 10
    queryset = Comment.objects.order_by('-ovr', '-like', '-timestamp')


# 【選手】コメントリスト（低評価順）
class CommnetListLowRatingView(ListView):
    model = Comment
    template_name = 'soccer/player/comment_list.html'
    paginate_by = 10
    queryset = Comment.objects.order_by('ovr', '-like', '-timestamp')


# 【選手】コメント投稿フォーム
class CommentFormView(CreateView):
    model = Comment
    template_name = 'soccer/player/comment_form.html'
    form_class = CommentForm

    def get_form_kwargs(self):
        kwargs = super(CommentFormView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def comment_save(self,form,player_pk):
        comment = form.save(commit=False)
        comment.player = get_object_or_404(Player, pk=player_pk)
        try:
            comment.user = views.get_current_user(self.request)
        except:
            pass
        comment.user_ip_address = views.get_ip(self.request)
        if comment.player.main_position == 'GK':
            comment.shoot = None
            comment.dribble = None
            comment.pas = None
            comment.defense = None
            comment.physical = None
            comment.speed = None
        else:
            comment.saving = None
            comment.handling = None
            comment.kick = None
            comment.positioning = None
            comment.reflexes = None
        comment.save()
        return redirect('soccer:player_detail', pk=player_pk)

    def comment_refuse(self,player_pk):
        messages.error(self.request, 'すでにコメントしているため投稿できません。')
        return redirect('soccer:comment_form', pk=player_pk)

    def form_valid(self,form):
        user_ip_address = views.get_ip(self.request)
        player_pk = self.kwargs['pk']
        player = get_object_or_404(Player, pk=player_pk)
        try:
            if self.request.user.is_authenticated:
                user_comment = Comment.objects.get(user=self.request.user, player=player)
            else:
                user_comment = Comment.objects.get(user_ip_address=user_ip_address, player=player)
            if user_comment.timestamp > (timezone.now() - timedelta(days=30)):
                return CommentFormView.comment_refuse(self,player_pk)
            else:
                return CommentFormView.comment_save(self,form,player_pk)
        except Comment.MultipleObjectsReturned:
            user_comment = Comment.objects.filter(user_ip_address=user_ip_address, player=player).first()
            if user_comment.timestamp > (timezone.now() - timedelta(days=30)):
                return CommentFormView.comment_refuse(self,player_pk)
            else:
                return CommentFormView.comment_save(self,form,player_pk)
        except Comment.DoesNotExist:
            return CommentFormView.comment_save(self,form,player_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_pk = self.kwargs['pk']
        context['player'] = get_object_or_404(Player, pk=player_pk)
        return context


# 【選手】コメントに対するいいね機能
def player_like(request,pk):
    ip = views.get_ip(request)
    player_comment = Comment.objects.get(pk=pk)
    if request.user.is_authenticated:
        user_filter_comment = LikeIpAddress.objects.filter(user=request.user, player_comment=player_comment)
    else:
        user_filter_comment = LikeIpAddress.objects.filter(ip=ip, player_comment=player_comment)
    if user_filter_comment:
        if request.user.is_authenticated:
            user_comment = LikeIpAddress.objects.get(user=request.user, player_comment=player_comment)
        else:
            user_comment = LikeIpAddress.objects.get(ip=ip, player_comment=player_comment)
        if user_comment.like_click_count < 10:
            user_comment.like_click_count += 1
            if user_comment.like_flg == '1':
                user_comment.like_flg = '0'
                user_comment.save()
                player_comment.like -= 1
                player_comment.save()
            else:
                user_comment.like_flg = '1'
                user_comment.save()
                player_comment.like += 1
                player_comment.save()
        else:
            user_comment.like_click_count = 10
            user_comment.save()
        return JsonResponse({"like":player_comment.like, "pk": player_comment.id, "count": user_comment.like_click_count})
    else:
        like = LikeIpAddress()
        like.ip = ip
        try:
            like.user = views.get_current_user(request)
        except:
            pass
        like.player = player_comment.player
        like.player_comment = player_comment
        like.comment_text = player_comment.text
        like.like_click_count += 1
        like.save()
        player_comment.like += 1
        player_comment.save()
        return JsonResponse({"like":player_comment.like, "pk": player_comment.id, "count": like.like_click_count})


# 【選手】コメント削除(※ログインユーザーのみ可能)
@login_required
def comment_remove(request, pk):
    player_comment = get_object_or_404(Comment, pk=pk)
    player_comment.delete()
    return redirect('soccer:player_detail', pk=player_comment.player.pk)


# 【選手】プロフィール更新リクエストフォーム
class PlayerUpdateRequestFormView(CreateView):
    model = PlayerUpdateRequest
    form_class = PlayerUpdateRequestForm
    template_name = "request/player_update_request_form.html"

    def get_form_kwargs(self):
        kwargs = super(PlayerUpdateRequestFormView,self).get_form_kwargs()
        kwargs['player_id'] =self.kwargs['pk']
        return kwargs

    def player_update_request_save(self,form,player_pk):
        request = form.save(commit=False)
        request.player_id = player_pk
        request.save()
        messages.success(self.request, 'プロフィールの更新リクエストが送信されました')
        return redirect('soccer:player_detail', pk=player_pk)
    
    def form_valid(self,form):
        subject = "【選手】更新リクエストが届きました"
        form_name = form.cleaned_data['name']
        form_league = form.cleaned_data['league']
        form_team = form.cleaned_data['team']
        form_area = form.cleaned_data['area']
        form_country = form.cleaned_data['country']
        form_birthday = form.cleaned_data['birthday']
        form_height = form.cleaned_data['height']
        form_foot = form.cleaned_data['foot']
        form_main_position = form.cleaned_data['main_position']
        form_second_position = form.cleaned_data['second_position']
        form_third_position = form.cleaned_data['third_position']
        message = F"""下記内容の選手更新リクエストが届きました。

━━━　更新リクエストの内容　━━━

名前：{form_name}
リーグ：{form_league}
チーム：{form_team}
地域：{form_area}
国籍：{form_country}
生年月日：{form_birthday}
身長：{form_height}
利き足：{form_foot}
メインポジション：{form_main_position}
セカンドポジション：{form_second_position}
サードポジション：{form_third_position}

━━━━━━━━━━━━━━━━━━

下記リンクより更新もしくは削除の対応を行ってください。
{settings.PROTOCOL}://{settings.DOMAIN}/{settings.DJANGO_ADMIN_URL}soccer/playerupdaterequest/
"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_email)
        player_pk = self.kwargs['pk']
        return PlayerUpdateRequestFormView.player_update_request_save(self,form,player_pk)


# 【選手】新規追加リクエストフォーム
class PlayerNewCreateRequestFormView(CreateView):
    model = PlayerNewCreateRequest
    form_class = PlayerNewCreateRequestForm
    template_name = "request/player_new_create_request_form.html"

    def player_new_create_request_save(self,form):
        request = form.save(commit=False)
        request.user_ip_address = views.get_ip(self.request)
        request.save()
        # messages.success(self.request, '監督の新規追加リクエストが送信されました')
        return redirect('soccer:player_request_result')

    def form_valid(self,form):
        subject = "【選手】新規追加リクエストが届きました"
        form_league = form.cleaned_data['league']
        form_team = form.cleaned_data['team']
        form_area = form.cleaned_data['area']
        form_country = form.cleaned_data['country']
        form_name = form.cleaned_data['name']
        form_birthday = form.cleaned_data['birthday']
        form_height = form.cleaned_data['height']
        form_foot = form.cleaned_data['foot']
        form_main_position = form.cleaned_data['main_position']
        form_second_position = form.cleaned_data['second_position']
        form_third_position = form.cleaned_data['third_position']
        message = F"""下記内容の選手追加リクエストが届きました。

━━━　新規追加リクエストの内容　━━━

名前：{form_name}
リーグ：{form_league}
チーム：{form_team}
地域：{form_area}
国籍：{form_country}
生年月日：{form_birthday}
身長：{form_height}
利き足：{form_foot}
メインポジション：{form_main_position}
セカンドポジション：{form_second_position}
サードポジション：{form_third_position}

━━━━━━━━━━━━━━━━━━━━

下記リンクより新規追加もしくは削除の対応を行ってください。
{settings.PROTOCOL}://{settings.DOMAIN}/{settings.DJANGO_ADMIN_URL}soccer/playernewcreaterequest/
"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_email)
        return PlayerNewCreateRequestFormView.player_new_create_request_save(self,form)
