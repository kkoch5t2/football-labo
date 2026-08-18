from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import CreateView

from django.db.models import Count, Avg, Q, F
from django.http import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.conf import settings
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib import messages

from datetime import timedelta
from django.utils import timezone

from django.http.response import JsonResponse

from soccer.forms import(
    ClubCommentForm,
    ClubUpdateRequestForm,
    ClubNewCreateRequestForm,
)

from soccer.models import(
    League,
    Team,
    ClubComment,
    ClubCommentLikeIpAddress,
    ClubUpdateRequest,
    ClubNewCreateRequest,
)

from soccer.views import views


# 【クラブ】トップページ
class ClubIndexView(ListView):
    template_name = 'soccer/club/club_index.html'
    model = Team
    paginate_by = 5

    queryset = Team.objects.exclude(league=9).annotate(
        num_comments=Count('club_comments')).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super(ClubIndexView, self).get_context_data(**kwargs)
        context.update({
            'comment_list': ClubComment.objects.all(),
        })
        return context


# 【クラブ】リーグリスト
class LeagueItemListView(ListView):
    template_name = 'soccer/club/league_item_list.html'
    queryset = League.objects.annotate(
        num_teams=Count('team'))


# 【クラブ】リーグごとのクラブリスト（最新順）
class LeagueClubView(ListView):
    model = Team
    template_name = 'soccer/club/league_club.html'
    paginate_by = 10
    queryset = Team.objects.annotate(
        num_comments=Count('club_comments')).order_by('-created_at')

    def get_queryset(self):
        league_slug = self.kwargs['league_slug']
        self.league = get_object_or_404(League.objects.exclude(slug='others'),slug=league_slug)
        qs = super().get_queryset().filter(league=self.league)
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league'] = self.league
        return context


# 【クラブ】リーグごとのクラブリスト（コメント数順）
class LeagueClubCommentCountView(ListView):
    model = Team
    template_name = 'soccer/club/league_club_comment_count.html'
    paginate_by = 10
    queryset = Team.objects.annotate(
        num_comments=Count('club_comments')).order_by('-num_comments','-created_at')

    def get_queryset(self):
        league_slug = self.kwargs['league_slug']
        self.league = get_object_or_404(League.objects.exclude(slug='others'),slug=league_slug)
        qs = super().get_queryset().filter(league=self.league)
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league'] = self.league
        return context


# 【クラブ】リーグごとのクラブリスト（平均総合評価順）
class LeagueClubAvgRatingView(ListView):
    model = Team
    template_name = 'soccer/club/league_club_avg_rating.html'
    paginate_by = 10
    queryset = Team.objects.annotate(
        num_comments=Count('club_comments'), avg_ovr=Avg('club_comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')

    def get_queryset(self):
        league_slug = self.kwargs['league_slug']
        self.league = get_object_or_404(League.objects.exclude(slug='others'),slug=league_slug)
        qs = super().get_queryset().filter(league=self.league)
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league'] = self.league
        return context


# 【クラブ】詳細（コメント最新順）
class ClubDetailView(DetailView):
    model = Team
    template_name = 'soccer/club/club_detail.html'
    queryset = Team.objects.annotate(
        num_comments=Count('club_comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(ClubDetailView, self).get_context_data(*args, **kwargs)
        page_number = self.request.GET.get('page')
        club_comments = context['team'].club_comments.all()
        paginator = Paginator(club_comments, per_page=10)
        context['club_comments'] = paginator.get_page(page_number)
        return context


# 【クラブ】詳細（コメントいいね数順）
class ClubDetailLikeCountView(DetailView):
    model = Team
    template_name = 'soccer/club/club_detail_like_count.html'
    queryset = Team.objects.annotate(
        num_comments=Count('club_comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(ClubDetailLikeCountView, self).get_context_data(*args, **kwargs)
        page_number = self.request.GET.get('page')
        club_comments = context['team'].club_comments.all().order_by('-like', '-timestamp')
        paginator = Paginator(club_comments, per_page=10)
        context['club_comments'] = paginator.get_page(page_number)
        return context


# 【クラブ】詳細（コメント高評価数順）
class ClubDetailHighRatingView(DetailView):
    model = Team
    template_name = 'soccer/club/club_detail_high_rating.html'
    queryset = Team.objects.annotate(
        num_comments=Count('club_comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(ClubDetailHighRatingView, self).get_context_data(*args, **kwargs)
        page_number = self.request.GET.get('page')
        club_comments = context['team'].club_comments.all().order_by('-ovr', '-like', '-timestamp')
        paginator = Paginator(club_comments, per_page=10)
        context['club_comments'] = paginator.get_page(page_number)
        return context


# 【クラブ】詳細（コメント低評価数順）
class ClubDetailLowRatingView(DetailView):
    model = Team
    template_name = 'soccer/club/club_detail_low_rating.html'
    queryset = Team.objects.annotate(
        num_comments=Count('club_comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(ClubDetailLowRatingView, self).get_context_data(*args, **kwargs)
        page_number = self.request.GET.get('page')
        club_comments = context['team'].club_comments.all().order_by('ovr', '-like', '-timestamp')
        paginator = Paginator(club_comments, per_page=10)
        context['club_comments'] = paginator.get_page(page_number)
        return context


# 【クラブ】クラブチームの検索機能
class SearchClubView(ListView):
    model = Team
    template_name = 'soccer/club/search_club.html'
    paginate_by = 10

    queryset = Team.objects.exclude(league=9).annotate(
        num_comments=Count('club_comments')).order_by( '-num_comments','-created_at')

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


# 【クラブ】コメントリスト（最新順）
class ClubCommnetListView(ListView):
    model = ClubComment
    template_name = 'soccer/club/club_comment_list.html'
    paginate_by = 10
    queryset = ClubComment.objects.order_by('-timestamp')


# 【クラブ】コメントリスト（いいね数順）
class ClubCommnetListLikeCountView(ListView):
    model = ClubComment
    template_name = 'soccer/club/club_comment_list_like_count.html'
    paginate_by = 10
    queryset = ClubComment.objects.order_by('-like', '-timestamp')


# 【クラブ】コメントリスト（高評価順）
class ClubCommnetListHighRatingView(ListView):
    model = ClubComment
    template_name = 'soccer/club/club_comment_list_high_rating.html'
    paginate_by = 10
    queryset = ClubComment.objects.order_by('-ovr', '-like', '-timestamp')


# 【クラブ】コメントリスト（低評価順）
class ClubCommnetListLowRatingView(ListView):
    model = ClubComment
    template_name = 'soccer/club/club_comment_list_low_rating.html'
    paginate_by = 10
    queryset = ClubComment.objects.order_by('ovr', '-like', '-timestamp')


# 【クラブ】コメント投稿フォーム
class ClubCommentFormView(CreateView):
    model = ClubComment
    form_class = ClubCommentForm
    template_name = 'soccer/club/club_comment_form.html'

    def get_form_kwargs(self):
        kwargs = super(ClubCommentFormView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def comment_save(self,form,team_slug):
        comment = form.save(commit=False)
        comment.team = get_object_or_404(Team, slug=team_slug)
        try:
            comment.user = views.get_current_user(self.request)
        except:
            pass
        comment.user_ip_address = views.get_ip(self.request)
        comment.save()
        return redirect('soccer:club_detail', slug=team_slug)

    def comment_refuse(self,team_slug):
        messages.error(self.request, 'すでにコメントしているため投稿できません。')
        return redirect('soccer:club_comment_form', slug=team_slug)

    def form_valid(self,form):
        user_ip_address = views.get_ip(self.request)
        team_slug = self.kwargs['slug']
        team = get_object_or_404(Team, slug=team_slug)
        try:
            if self.request.user.is_authenticated:
                user_team_comment = ClubComment.objects.get(user=self.request.user, team=team)
            else:
                user_team_comment = ClubComment.objects.get(user_ip_address=user_ip_address, team=team)
            if user_team_comment.timestamp > (timezone.now() - timedelta(days=30)):
                return ClubCommentFormView.comment_refuse(self,team_slug)
            else:
                return ClubCommentFormView.comment_save(self,form,team_slug)
        except ClubComment.MultipleObjectsReturned:
            user_team_comment = ClubComment.objects.filter(user_ip_address=user_ip_address, team=team).first()
            if user_team_comment.timestamp > (timezone.now() - timedelta(days=30)):
                return ClubCommentFormView.comment_refuse(self,team_slug)
            else:
                return ClubCommentFormView.comment_save(self,form,team_slug)
        except ClubComment.DoesNotExist:
            return ClubCommentFormView.comment_save(self,form,team_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_slug = self.kwargs['slug']
        context['team'] = get_object_or_404(Team, slug=team_slug)
        return context


# 【クラブ】コメントに対するいいね機能
def club_like(request,pk):
    ip = views.get_ip(request)
    club_comment = ClubComment.objects.get(pk=pk)
    if request.user.is_authenticated:
        user_filter_comment = ClubCommentLikeIpAddress.objects.filter(user=request.user, club_comment=club_comment)
    else:
        user_filter_comment = ClubCommentLikeIpAddress.objects.filter(ip=ip, club_comment=club_comment)
    if user_filter_comment:
        if request.user.is_authenticated:
            user_comment = ClubCommentLikeIpAddress.objects.get(user=request.user, club_comment=club_comment)
        else:
            user_comment = ClubCommentLikeIpAddress.objects.get(ip=ip, club_comment=club_comment)
        if user_comment.like_click_count < 10:
            user_comment.like_click_count += 1
            if user_comment.like_flg == '1':
                user_comment.like_flg = '0'
                user_comment.save()
                club_comment.like -= 1
                club_comment.save()
            else:
                user_comment.like_flg = '1'
                user_comment.save()
                club_comment.like += 1
                club_comment.save()
        else:
            user_comment.like_click_count = 10
            user_comment.save()
        return JsonResponse({"like":club_comment.like, "pk": club_comment.id, "count": user_comment.like_click_count})
    else:
        like = ClubCommentLikeIpAddress()
        like.ip = ip
        try:
            like.user = views.get_current_user(request)
        except:
            pass
        like.league = club_comment.team.league
        like.team = club_comment.team
        like.club_comment = club_comment
        like.comment_text = club_comment.text
        like.like_click_count += 1
        like.save()
        club_comment.like += 1
        club_comment.save()
        return JsonResponse({"like":club_comment.like, "pk": club_comment.id, "count": like.like_click_count})


# 【クラブ】コメント削除(※ログインユーザーのみ可能)
@login_required
def club_comment_remove(request, pk):
    club_comment = get_object_or_404(ClubComment, pk=pk)
    club_comment.delete()
    return redirect('soccer:club_detail', slug=club_comment.team.slug)


# 【クラブ】プロフィール更新リクエストフォーム
class ClubUpdateRequestFormView(CreateView):
    model = ClubUpdateRequest
    form_class = ClubUpdateRequestForm
    template_name = "request/club_team_update_request_form.html"

    def get_form_kwargs(self):
        kwargs = super(ClubUpdateRequestFormView,self).get_form_kwargs()
        kwargs['team_slug'] =self.kwargs['slug']
        return kwargs

    def club_team_update_request_save(self,form,slug):
        request = form.save(commit=False)
        obj = Team.objects.get(slug=slug)
        request.team_id = obj.id
        request.save()
        messages.success(self.request, 'プロフィールの更新リクエストが送信されました')
        return redirect('soccer:club_detail', slug=slug)
    
    def form_valid(self,form):
        subject = "【クラブチーム】更新リクエストが届きました"
        form_name = form.cleaned_data['name']
        form_league = form.cleaned_data['league']
        form_year_established = form.cleaned_data['year_established']
        form_home_town = form.cleaned_data['home_town']
        message = F"""下記内容のクラブチーム更新リクエストが届きました。

━━━　更新リクエストの内容　━━━

名前：{form_name}
リーグ：{form_league}
創設年：{form_year_established}
ホームタウン：{form_home_town}

━━━━━━━━━━━━━━━━━━

下記リンクより更新もしくは削除の対応を行ってください。
{settings.PROTOCOL}://{settings.DOMAIN}/{settings.DJANGO_ADMIN_URL}soccer/clubupdaterequest/
"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_email)
        club_team_slug = self.kwargs['slug']
        return ClubUpdateRequestFormView.club_team_update_request_save(self,form,club_team_slug)
    

# 【クラブ】新規追加リクエストフォーム
class ClubNewCreateRequestFormView(CreateView):
    model = ClubNewCreateRequest
    form_class = ClubNewCreateRequestForm
    template_name = "request/club_team_new_create_request_form.html"

    def club_team_new_create_request_save(self,form):
        request = form.save(commit=False)
        request.user_ip_address = views.get_ip(self.request)
        request.save()
        # messages.success(self.request, '監督の新規追加リクエストが送信されました')
        return redirect('soccer:club_team_request_result')

    def form_valid(self,form):
        subject = "【クラブチーム】新規追加リクエストが届きました"
        form_name = form.cleaned_data['name']
        form_league = form.cleaned_data['league']
        form_year_established = form.cleaned_data['year_established']
        form_home_town = form.cleaned_data['home_town']
        message = F"""下記内容のクラブチーム追加リクエストが届きました。

━━━　新規追加リクエストの内容　━━━

名前：{form_name}
リーグ：{form_league}
創設年：{form_year_established}
ホームタウン：{form_home_town}

━━━━━━━━━━━━━━━━━━━━

下記リンクより新規追加もしくは削除の対応を行ってください。
{settings.PROTOCOL}://{settings.DOMAIN}/{settings.DJANGO_ADMIN_URL}soccer/clubnewcreaterequest/
"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_email)
        return ClubNewCreateRequestFormView.club_team_new_create_request_save(self,form)
