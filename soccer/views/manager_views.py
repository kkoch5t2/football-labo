from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import CreateView

from django.db.models import Count, Avg, Q, F
from django.http import Http404, HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.conf import settings
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib import messages

from datetime import timedelta
from django.utils import timezone

import json
from django.http.response import JsonResponse

from soccer.forms import(
    ManagerCommentForm,
    ManagerUpdateRequestForm,
    ManagerNewCreateRequestForm,
)

from soccer.models import(
    League,
    Team,
    Area,
    Country,
    Manager,
    ManagerComment,
    ManagerLikeIpAddress,
    ManagerUpdateRequest,
    ManagerNewCreateRequest,
)

from soccer.views import views


# 【監督】トップページ
class ManagerIndexView(ListView):
    template_name = 'soccer/manager/manager_index.html'
    model = Manager
    paginate_by = 5

    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments')).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super(ManagerIndexView, self).get_context_data(**kwargs)
        context.update({
            'comment_list': ManagerComment.objects.all(),
        })
        return context


# 【監督】リスト（最新順）
class ManagerListView(ListView):
    model = Manager
    template_name = 'soccer/manager/manager_list.html'
    paginate_by = 10
    # 監督ごとのコメント数を取得＆ページ作成日時順（降順）に並べる
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments')).order_by('-created_at')


# 【監督】リスト（コメント数順）
class ManagerListCommentCountView(ListView):
    model = Manager
    template_name = 'soccer/manager/manager_list_comment_count.html'
    paginate_by = 10
    # 監督ごとのコメント数を取得＆コメント数（降順）、ページ作成日時（降順）の順に並べる
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments')).order_by('-num_comments', '-created_at')


# 【監督】リスト（平均総合評価順）
class ManagerListAvgRatingView(ListView):
    model = Manager
    template_name = 'soccer/manager/manager_list_avg_rating.html'
    paginate_by = 10
    # 監督ごとのコメント数と平均総合評価の値を取得＆平均総合評価（降順）、コメント数（降順）、ページ作成日時（降順）の順に並べる
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments'), avg_ovr=Avg('manager_comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')


# 【監督】地域リスト
class ManagerAreaView(ListView):
    template_name = 'soccer/manager/manager_area_list.html'
    # 地域ごとの国数を取得
    queryset = Area.objects.annotate(num_countries=Count('country'))


# 【監督】地域ごとの国リスト
class ManagerAreaCountryView(ListView):
    model = Country
    template_name = 'soccer/manager/manager_area_country.html'
    # 出身国ごとの監督数を取得
    queryset = Country.objects.annotate(
        num_managers=Count('manager')).order_by('-num_managers','name')

    '''
    get時に指定されたarea_slugと一致するslugのオブジェクトを取得。
    取得したデータをself.areaに代入し、self.areaと一致するareaを返す。
    '''
    def get_queryset(self):
        area_slug = self.kwargs['area_slug']
        self.area = get_object_or_404(Area, slug=area_slug)
        qs = super().get_queryset().filter(area=self.area)
        return qs

    # context（辞書型）に上記メソッド内の変数self.areaを代入
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['area'] = self.area
        return context


# 【監督】国ごとの監督リスト（最新順）
class CountryManagerView(ListView):
    model = Manager
    template_name = 'soccer/manager/country_manager_list.html'
    paginate_by = 10
    # 各監督のコメント数をカウント
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments')).order_by('-created_at')

    '''
    get時に指定されたmanager_country_slugと一致するslugのオブジェクトを取得。
    取得したデータをself.countryに代入し、self.countryと一致するcountryを返す。
    '''
    def get_queryset(self):
        manager_country_slug = self.kwargs['manager_country_slug']
        self.country = get_object_or_404(Country, slug=manager_country_slug)
        qs = super().get_queryset().filter(country=self.country)
        return qs

    # context（辞書型）に上記メソッド内の変数self.countryを代入
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.country
        return context


# 【監督】国ごとの監督リスト（コメント数順）
class CountryManagerCommentCountView(ListView):
    model = Manager
    template_name = 'soccer/manager/country_manager_list_comment_count.html'
    paginate_by = 10
    # 各監督のコメント数をカウント
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments')).order_by('-num_comments','-created_at')

    '''
    get時に指定されたmanager_country_slugと一致するslugのオブジェクトを取得。
    取得したデータをself.countryに代入し、self.countryと一致するcountryを返す。
    '''
    def get_queryset(self):
        manager_country_slug = self.kwargs['manager_country_slug']
        self.manager_country = get_object_or_404(Country, slug=manager_country_slug)
        qs = super().get_queryset().filter(country=self.manager_country)
        return qs

    # context（辞書型）に上記メソッド内の変数self.countryを代入
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.manager_country
        return context


# 【監督】国ごとの監督リスト（平均総合評価順）
class CountryManagerAvgRatingView(ListView):
    model = Manager
    template_name = 'soccer/manager/country_manager_list_avg_rating.html'
    paginate_by = 10
    # 各監督のコメント数をカウント
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments'), avg_ovr=Avg('manager_comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')

    '''
    get時に指定されたmanager_country_slugと一致するslugのオブジェクトを取得。
    取得したデータをself.countryに代入し、self.countryと一致するcountryを返す。
    '''
    def get_queryset(self):
        manager_country_slug = self.kwargs['manager_country_slug']
        self.manager_country = get_object_or_404(Country, slug=manager_country_slug)
        qs = super().get_queryset().filter(country=self.manager_country)
        return qs

    # context（辞書型）に上記メソッド内の変数self.countryを代入
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.manager_country
        return context


# 【監督】リーグリスト
class ManagerLeagueListView(ListView):
    template_name = 'soccer/manager/manager_league_list.html'
    queryset = League.objects.annotate(num_teams=Count('team'))


# 【監督】リーグごとのチームリスト
class ManagerLeagueTeamView(ListView):
    model = Team
    template_name = 'soccer/manager/manager_league_team.html'
    queryset = Team.objects.annotate(
        num_managers=Count('manager')).order_by('-num_managers', 'name')
    
    '''
    get時に指定されたleagueと一致するslugのオブジェクトを取得。
    取得したデータをself.manager_leagueに代入し、self.manager_leagueと一致するmanager_leagueを返す。
    '''
    def get_queryset(self):
        manager_league_slug = self.kwargs['manager_league_slug']
        self.manager_league = get_object_or_404(League, slug=manager_league_slug)
        qs = super().get_queryset().filter(league=self.manager_league)
        return qs

    # context（辞書型）に上記メソッド内の変数self.manager_leagueを代入
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league'] = self.manager_league
        return context


# 【監督】リーグごとの監督リスト
class TeamManagerView(ListView):
    model = Manager
    template_name = 'soccer/manager/team_manager_list.html'
    paginate_by = 10
    # 各監督のコメント数をカウント
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments')).order_by('-created_at')

    '''
    get時に指定されたteam_type_slugと一致するslugのオブジェクトを取得。
    取得したデータをself.team_typeに代入し、self.team_typeと一致するteam_typeを返す。
    '''
    def get_queryset(self):
        manager_team_slug = self.kwargs['manager_team_slug']
        self.manager_team = get_object_or_404(Team, slug=manager_team_slug)
        qs = super().get_queryset().filter(team=self.manager_team)
        return qs

    # context（辞書型）に上記メソッド内の変数self.teamを代入
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.manager_team
        return context
    

# 【監督】リーグや地域ごとの監督リスト（コメント数順）
class TeamManagerCommentCountView(ListView):
    model = Manager
    template_name = 'soccer/manager/team_manager_list_comment_count.html'
    paginate_by = 10
    # 各監督のコメント数をカウント
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments')).order_by('-num_comments','-created_at')

    '''
    get時に指定されたteam_type_slugと一致するslugのオブジェクトを取得。
    取得したデータをself.team_typeに代入し、self.team_typeと一致するteam_typeを返す。
    '''
    def get_queryset(self):
        manager_team_slug = self.kwargs['manager_team_slug']
        self.manager_team = get_object_or_404(Team, slug=manager_team_slug)
        qs = super().get_queryset().filter(team=self.manager_team)
        return qs

    # context（辞書型）に上記メソッド内の変数self.teamを代入
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.manager_team
        return context


# 【監督】リーグや地域ごとの監督リスト（平均総合評価順）
class TeamManagerAvgRatingView(ListView):
    model = Manager
    template_name = 'soccer/manager/team_manager_list_avg_rating.html'
    paginate_by = 10
    # 各監督のコメント数をカウント
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments'), avg_ovr=Avg('manager_comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')

    '''
    get時に指定されたteam_type_slugと一致するslugのオブジェクトを取得。
    取得したデータをself.team_typeに代入し、self.team_typeと一致するteam_typeを返す。
    '''
    def get_queryset(self):
        manager_team_slug = self.kwargs['manager_team_slug']
        self.manager_team = get_object_or_404(Team, slug=manager_team_slug)
        qs = super().get_queryset().filter(team=self.manager_team)
        return qs

    # context（辞書型）に上記メソッド内の変数self.teamを代入
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.manager_team
        return context


# 【監督】詳細（コメント最新順）
class ManagerDetailView(DetailView):
    model = Manager
    template_name = 'soccer/manager/manager_detail.html'
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments'))

    # オブジェクトを取得
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # 投稿が公開されてない場合は404エラーを送出する
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    # コメントのページング機能を設定
    def get_context_data(self, **kwargs):
        context = super(ManagerDetailView, self).get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        manager_comments = context['manager'].manager_comments.all()
        paginator = Paginator(manager_comments, per_page=10)
        context['manager_comments'] = paginator.get_page(page_number)
        return context


# 【監督】詳細（コメントいいね数順）
class ManagerDetailLikeCountView(DetailView):
    model = Manager
    template_name = 'soccer/manager/manager_detail_like_count.html'
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments'))

    # オブジェクトを取得
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # 投稿が公開されてない場合は404エラーを送出する
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    # コメントのページング機能を設定
    def get_context_data(self, **kwargs):
        context = super(ManagerDetailLikeCountView, self).get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        manager_comments = context['manager'].manager_comments.all().order_by('-like','-timestamp')
        paginator = Paginator(manager_comments, per_page=10)
        context['manager_comments'] = paginator.get_page(page_number)
        return context


# 【監督】詳細（コメント高評価順）
class ManagerDetailHighRatingView(DetailView):
    model = Manager
    template_name = 'soccer/manager/manager_detail_high_rating.html'
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments'))

    # オブジェクトを取得
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # 投稿が公開されてない場合は404エラーを送出する
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    # コメントのページング機能を設定
    def get_context_data(self, **kwargs):
        context = super(ManagerDetailHighRatingView, self).get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        manager_comments = context['manager'].manager_comments.all().order_by('-ovr', '-like','-timestamp')
        paginator = Paginator(manager_comments, per_page=10)
        context['manager_comments'] = paginator.get_page(page_number)
        return context


# 【監督】詳細（コメント低評価順）
class ManagerDetailLowRatingView(DetailView):
    model = Manager
    template_name = 'soccer/manager/manager_detail_low_rating.html'
    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments'))

    # オブジェクトを取得
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # 投稿が公開されてない場合は404エラーを送出する
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    # コメントのページング機能を設定
    def get_context_data(self, **kwargs):
        context = super(ManagerDetailLowRatingView, self).get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        manager_comments = context['manager'].manager_comments.all().order_by('ovr', '-like','-timestamp')
        paginator = Paginator(manager_comments, per_page=10)
        context['manager_comments'] = paginator.get_page(page_number)
        return context


# 【監督】監督の検索機能
class SearchManagerView(ListView):
    model = Manager
    template_name = 'soccer/manager/search_manager.html'
    paginate_by = 10

    queryset = Manager.objects.annotate(
        num_comments=Count('manager_comments')).order_by( '-num_comments','-created_at')

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


# 【監督】コメントリスト（最新順）
class ManagerCommnetListView(ListView):
    model = ManagerComment
    template_name = 'soccer/manager/manager_comment_list.html'
    paginate_by = 10    
    queryset = ManagerComment.objects.order_by('-timestamp')


# 【監督】コメントリスト（いいね数順）
class ManagerCommnetListLikeCountView(ListView):
    model = ManagerComment
    template_name = 'soccer/manager/manager_comment_list_like_count.html'
    paginate_by = 10    
    queryset = ManagerComment.objects.order_by('-like', '-timestamp')


# 【監督】コメントリスト（高評価順）
class ManagerCommnetListHighRatingView(ListView):
    model = ManagerComment
    template_name = 'soccer/manager/manager_comment_list_high_rating.html'
    paginate_by = 10
    queryset = ManagerComment.objects.order_by('-ovr', '-like', '-timestamp')


# 【監督】コメントリスト（低評価順）
class ManagerCommnetListLowRatingView(ListView):
    model = ManagerComment
    template_name = 'soccer/manager/manager_comment_list_low_rating.html'
    paginate_by = 10    
    queryset = ManagerComment.objects.order_by('ovr', '-like', '-timestamp')


# 【監督】コメント投稿フォーム
class ManagerCommentFormView(CreateView):
    model = ManagerComment
    form_class = ManagerCommentForm
    template_name = 'soccer/manager/manager_comment_form.html'

    def get_form_kwargs(self):
        kwargs = super(ManagerCommentFormView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def comment_save(self,form,manager_pk):
        comment = form.save(commit=False)
        comment.manager = get_object_or_404(Manager, pk=manager_pk)
        try:
            comment.user = views.get_current_user(self.request)
        except:
            pass
        comment.user_ip_address = views.get_ip(self.request)
        comment.save()
        return redirect('soccer:manager_detail', pk=manager_pk)

    def comment_refuse(self, manager_pk):
        messages.error(self.request, 'すでにコメントしているため投稿できません。')
        return redirect('soccer:manager_comment_form', pk=manager_pk)

    def form_valid(self,form):
        user_ip_address = views.get_ip(self.request)
        manager_pk = self.kwargs['pk']
        manager = get_object_or_404(Manager, pk=manager_pk)    
        try:
            if self.request.user.is_authenticated:
                user_comment = ManagerComment.objects.get(user=self.request.user, manager=manager)
            else:
                user_comment = ManagerComment.objects.get(user_ip_address=user_ip_address, manager=manager)
            if user_comment.timestamp > (timezone.now() - timedelta(days=30)):
                return ManagerCommentFormView.comment_refuse(self, manager_pk)
            else:
                return ManagerCommentFormView.comment_save(self,form,manager_pk)
        except ManagerComment.MultipleObjectsReturned:
            user_comment = ManagerComment.objects.filter(user_ip_address=user_ip_address, manager=manager).first()
            if user_comment.timestamp > (timezone.now() - timedelta(days=30)):
                return ManagerCommentFormView.comment_refuse(self, manager_pk)
            else:
                return ManagerCommentFormView.comment_save(self,form,manager_pk)
        except ManagerComment.DoesNotExist:
            return ManagerCommentFormView.comment_save(self,form,manager_pk)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager_pk = self.kwargs['pk']
        context['manager'] = get_object_or_404(Manager, pk=manager_pk)
        return context


# 【監督】コメントに対するいいね機能
def manager_like(request,pk):
    ip = views.get_ip(request)
    manager_comment = ManagerComment.objects.get(pk=pk)
    if request.user.is_authenticated:
        user_filter_comment = ManagerLikeIpAddress.objects.filter(user=request.user, manager_comment=manager_comment)
    else:
        user_filter_comment = ManagerLikeIpAddress.objects.filter(ip=ip, manager_comment=manager_comment)
    if user_filter_comment:
        if request.user.is_authenticated:
            user_comment = ManagerLikeIpAddress.objects.get(user=request.user, manager_comment=manager_comment)
        else:
            user_comment = ManagerLikeIpAddress.objects.get(ip=ip, manager_comment=manager_comment)
        if user_comment.like_click_count < 10:
            user_comment.like_click_count += 1
            if user_comment.like_flg == '1':
                user_comment.like_flg = '0'
                user_comment.save()
                manager_comment.like -= 1
                manager_comment.save()
            else:
                user_comment.like_flg = '1'
                user_comment.save()
                manager_comment.like += 1
                manager_comment.save()
        else:
            user_comment.like_click_count = 10
            user_comment.save()
        return JsonResponse({"like":manager_comment.like, "pk": manager_comment.id, "count": user_comment.like_click_count})
    else:
        like = ManagerLikeIpAddress()
        like.ip = ip
        try:
            like.user = views.get_current_user(request)
        except:
            pass
        like.manager = manager_comment.manager
        like.manager_comment = manager_comment
        like.comment_text = manager_comment.text
        like.like_click_count += 1
        like.save()
        manager_comment.like += 1
        manager_comment.save()
        return JsonResponse({"like":manager_comment.like, "pk": manager_comment.id, "count": like.like_click_count})


# 【監督】コメント削除(※ログインユーザーのみ可能)
@login_required
def manager_comment_remove(request, pk):
    manager_comment = get_object_or_404(ManagerComment, pk=pk)
    manager_comment.delete()
    return redirect('soccer:manager_detail', pk=manager_comment.manager.pk)


# 【監督|管理画面】子カテゴリ(リーグ、地域など)の諸設定
def get_manager_team(request):
    id = request.GET.get('id', '')
    result = list(Team.objects.filter(
        league_id=int(id)).values('id', 'name'))
    return HttpResponse(json.dumps(result), content_type="application/json")


# 【監督|管理画面】出身国の諸設定
def get_manager_country(request):
    id = request.GET.get('id', '')
    result = list(Country.objects.filter(
        area_id=int(id)).values('id', 'name'))
    return HttpResponse(json.dumps(result), content_type="application/json")


# 【監督】プロフィール更新リクエストフォーム
class ManagerUpdateRequestFormView(CreateView):
    model = ManagerUpdateRequest
    form_class = ManagerUpdateRequestForm
    template_name = "request/manager_update_request_form.html"

    def get_form_kwargs(self):
        kwargs = super(ManagerUpdateRequestFormView,self).get_form_kwargs()
        kwargs['manager_id'] =self.kwargs['pk']
        return kwargs

    def manager_update_request_save(self,form,manager_pk):
        request = form.save(commit=False)
        request.manager_id = manager_pk
        request.save()
        messages.success(self.request, 'プロフィールの更新リクエストが送信されました')
        return redirect('soccer:manager_detail', pk=manager_pk)
    
    def form_valid(self,form):
        subject = "【監督】更新リクエストが届きました"
        form_name = form.cleaned_data['name']
        form_league = form.cleaned_data['league']
        form_team = form.cleaned_data['team']
        form_area = form.cleaned_data['area']
        form_country = form.cleaned_data['country']
        form_birthday = form.cleaned_data['birthday']
        message = F"""下記内容の監督更新リクエストが届きました。

━━━　更新リクエストの内容　━━━

名前：{form_name}
リーグ：{form_league}
チーム：{form_team}
地域：{form_area}
国籍：{form_country}
生年月日：{form_birthday}

━━━━━━━━━━━━━━━━━━

下記リンクより更新もしくは削除の対応を行ってください。
{settings.PROTOCOL}://{settings.DOMAIN}/{settings.DJANGO_ADMIN_URL}soccer/managerupdaterequest/
"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_email)
        manager_pk = self.kwargs['pk']
        return ManagerUpdateRequestFormView.manager_update_request_save(self,form,manager_pk)


# 【監督】新規追加リクエストフォーム
class ManagerNewCreateRequestFormView(CreateView):
    model = ManagerNewCreateRequest
    form_class = ManagerNewCreateRequestForm
    template_name = "request/manager_new_create_request_form.html"
    success_url = "result/"

    def manager_new_create_request_save(self,form):
        request = form.save(commit=False)
        request.user_ip_address = views.get_ip(self.request)
        request.save()
        # messages.success(self.request, '監督の新規追加リクエストが送信されました')
        return redirect('soccer:manager_request_result')

    def form_valid(self,form):
        subject = "【監督】新規追加リクエストが届きました"
        form_name = form.cleaned_data['name']
        form_league = form.cleaned_data['league']
        form_team = form.cleaned_data['team']
        form_area = form.cleaned_data['area']
        form_country = form.cleaned_data['country']
        form_birthday = form.cleaned_data['birthday']
        message = F"""下記内容の監督追加リクエストが届きました。

━━━　新規追加リクエストの内容　━━━

名前：{form_name}
リーグ：{form_league}
チーム：{form_team}
地域：{form_area}
国籍：{form_country}
生年月日：{form_birthday}

━━━━━━━━━━━━━━━━━━━━

下記リンクより新規追加もしくは削除の対応を行ってください。
{settings.PROTOCOL}://{settings.DOMAIN}/{settings.DJANGO_ADMIN_URL}soccer/managernewcreaterequest/
"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_email)
        return ManagerNewCreateRequestFormView.manager_new_create_request_save(self,form)