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
    NationalCommentForm,
    NationalUpdateRequestForm,
    NationalNewCreateRequestForm,
)

from soccer.models import(
    Area,
    Country,
    NationalComment,
    NationalCommentLikeIpAddress,
    NationalUpdateRequest,
    NationalNewCreateRequest,
)

from soccer.views import views


# 【代表】トップページ
class NationalIndexView(ListView):
    template_name = 'soccer/national/national_index.html'
    model = Country
    paginate_by = 5

    queryset = Country.objects.annotate(
        num_comments=Count('national_comments')).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super(NationalIndexView, self).get_context_data(**kwargs)
        context.update({
            'comment_list': NationalComment.objects.all(),
        })
        return context


# 【代表】地域リスト
class AreaItemListView(ListView):
    template_name = 'soccer/national/area_item_list.html'
    queryset = Area.objects.annotate(
        num_countries=Count('country'))


# 【代表】地域ごとの国リスト（最新順）
class AreaNationalView(ListView):
    model = Country
    template_name = 'soccer/national/area_national.html'
    paginate_by = 10
    queryset = Country.objects.annotate(
        num_comments=Count('national_comments')).order_by('-created_at')
    
    def get_queryset(self):
        area_slug = self.kwargs['area_slug']
        self.area = get_object_or_404(Area, slug=area_slug)
        qs = super().get_queryset().filter(area=self.area)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['area'] = self.area
        return context


# 【代表】地域ごとの国リスト（コメント数順）
class AreaNationalCommentCountView(ListView):
    model = Country
    template_name = 'soccer/national/area_national.html'
    paginate_by = 10
    queryset = Country.objects.annotate(
        num_comments=Count('national_comments')).order_by('-num_comments','-created_at')
    
    def get_queryset(self):
        area_slug = self.kwargs['area_slug']
        self.area = get_object_or_404(Area, slug=area_slug)
        qs = super().get_queryset().filter(area=self.area)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['area'] = self.area
        return context


# 【代表】地域ごとの国リスト（平均総合評価順）
class AreaNationalAvgRatingView(ListView):
    model = Country
    template_name = 'soccer/national/area_national.html'
    paginate_by = 10
    queryset = Country.objects.annotate(
        num_comments=Count('national_comments'), avg_ovr=Avg('national_comments__ovr')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-created_at')
    
    def get_queryset(self):
        area_slug = self.kwargs['area_slug']
        self.area = get_object_or_404(Area, slug=area_slug)
        qs = super().get_queryset().filter(area=self.area)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['area'] = self.area
        return context


# 【代表】詳細（コメント最新順）
class NationalDetailView(DetailView):
    model = Country
    template_name = 'soccer/national/national_detail.html'
    queryset = Country.objects.annotate(
        num_comments=Count('national_comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(NationalDetailView, self).get_context_data(*args, **kwargs)
        page_number = self.request.GET.get('page')
        national_comments = context['country'].national_comments.all()
        paginator = Paginator(national_comments, per_page=10)
        context['national_comments'] = paginator.get_page(page_number)
        return context


# 【代表】詳細（コメントいいね数順）
class NationalDetailLikeCountView(DetailView):
    model = Country
    template_name = 'soccer/national/national_detail.html'
    queryset = Country.objects.annotate(
        num_comments=Count('national_comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(NationalDetailLikeCountView, self).get_context_data(*args, **kwargs)
        page_number = self.request.GET.get('page')
        national_comments = context['country'].national_comments.all().order_by('-like', '-timestamp')
        paginator = Paginator(national_comments, per_page=10)
        context['national_comments'] = paginator.get_page(page_number)
        return context


# 【代表】詳細（コメント高評価順）
class NationalDetailHighRatingView(DetailView):
    model = Country
    template_name = 'soccer/national/national_detail.html'
    queryset = Country.objects.annotate(
        num_comments=Count('national_comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(NationalDetailHighRatingView, self).get_context_data(*args, **kwargs)
        page_number = self.request.GET.get('page')
        national_comments = context['country'].national_comments.all().order_by('-ovr', '-like', '-timestamp')
        paginator = Paginator(national_comments, per_page=10)
        context['national_comments'] = paginator.get_page(page_number)
        return context


# 【代表】詳細（コメント低評価順）
class NationalDetailLowRatingView(DetailView):
    model = Country
    template_name = 'soccer/national/national_detail.html'
    queryset = Country.objects.annotate(
        num_comments=Count('national_comments'))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(NationalDetailLowRatingView, self).get_context_data(*args, **kwargs)
        page_number = self.request.GET.get('page')
        national_comments = context['country'].national_comments.all().order_by('ovr', '-like', '-timestamp')
        paginator = Paginator(national_comments, per_page=10)
        context['national_comments'] = paginator.get_page(page_number)
        return context


# 【代表】代表チームの検索機能
class SearchNationalView(ListView):
    model = Country
    template_name = 'soccer/national/search_national.html'
    paginate_by = 10

    queryset = Country.objects.annotate(
        num_comments=Count('national_comments')).order_by( '-num_comments','-created_at')

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


# 【代表】コメントリスト（最新順）
class NationalCommnetListView(ListView):
    model = NationalComment
    template_name = 'soccer/national/national_comment_list.html'
    paginate_by = 10
    queryset = NationalComment.objects.order_by('-timestamp')


# 【代表】コメントリスト（いいね数順）
class NationalCommnetListLikeCountView(ListView):
    model = NationalComment
    template_name = 'soccer/national/national_comment_list.html'
    paginate_by = 10
    queryset = NationalComment.objects.order_by('-like', '-timestamp')


# 【代表】コメントリスト（高評価順）
class NationalCommnetListHighRatingView(ListView):
    model = NationalComment
    template_name = 'soccer/national/national_comment_list.html'
    paginate_by = 10
    queryset = NationalComment.objects.order_by('-ovr', '-like', '-timestamp')


# 【代表】コメントリスト（低評価順）
class NationalCommnetListLowRatingView(ListView):
    model = NationalComment
    template_name = 'soccer/national/national_comment_list.html'
    paginate_by = 10
    queryset = NationalComment.objects.order_by('ovr', '-like', '-timestamp')


# 【代表】コメント投稿フォーム
class NationalCommentFormView(CreateView):
    model = NationalComment
    form_class = NationalCommentForm
    template_name = 'soccer/national/national_comment_form.html'

    def get_form_kwargs(self):
        kwargs = super(NationalCommentFormView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def comment_save(self,form,country_slug):
        comment = form.save(commit=False)
        comment.country = get_object_or_404(Country, slug=country_slug)
        try:
            comment.user = views.get_current_user(self.request)
        except:
            pass
        comment.user_ip_address = views.get_ip(self.request)
        comment.save()
        return redirect('soccer:national_detail', slug=country_slug)

    def comment_refuse(self,country_slug):
        messages.error(self.request, 'すでにコメントしているため投稿できません。')
        return redirect('soccer:national_comment_form',slug=country_slug)

    def form_valid(self,form):
        user_ip_address = views.get_ip(self.request)
        country_slug = self.kwargs['slug']
        country = get_object_or_404(Country, slug=country_slug)
        
        try:
            if self.request.user.is_authenticated:
                user_country_comment = NationalComment.objects.get(user=self.request.user, country=country)
            else:
                user_country_comment = NationalComment.objects.get(user_ip_address=user_ip_address, country=country)
            if user_country_comment.timestamp > (timezone.now() - timedelta(days=30)):
                return NationalCommentFormView.comment_refuse(self,country_slug)
            else:
                return NationalCommentFormView.comment_save(self,form,country_slug)
        except NationalComment.MultipleObjectsReturned:
            user_country_comment = NationalComment.objects.filter(user_ip_address=user_ip_address, country=country).first()
            if user_country_comment.timestamp > (timezone.now() - timedelta(days=30)):
                return NationalCommentFormView.comment_refuse(self,country_slug)
            else:
                return NationalCommentFormView.comment_save(self,form,country_slug)
        except NationalComment.DoesNotExist:
            return NationalCommentFormView.comment_save(self,form,country_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country_slug = self.kwargs['slug']
        context['country'] = get_object_or_404(Country, slug=country_slug)
        return context


# 【代表】コメントに対するいいね機能
def national_like(request,pk):
    ip = views.get_ip(request)
    national_comment = NationalComment.objects.get(pk=pk)
    if request.user.is_authenticated:
        user_filter_comment = NationalCommentLikeIpAddress.objects.filter(user=request.user, national_comment=national_comment)
    else:
        user_filter_comment = NationalCommentLikeIpAddress.objects.filter(ip=ip, national_comment=national_comment)
    if user_filter_comment:
        if request.user.is_authenticated:
            user_comment = NationalCommentLikeIpAddress.objects.get(user=request.user, national_comment=national_comment)
        else:
            user_comment = NationalCommentLikeIpAddress.objects.get(ip=ip, national_comment=national_comment)
        if user_comment.like_click_count < 10:
            user_comment.like_click_count += 1
            if user_comment.like_flg == '1':
                user_comment.like_flg = '0'
                user_comment.save()
                national_comment.like -= 1
                national_comment.save()
            else:
                user_comment.like_flg = '1'
                user_comment.save()
                national_comment.like += 1
                national_comment.save()
        else:
            user_comment.like_click_count = 10
            user_comment.save()
        return JsonResponse({"like":national_comment.like, "pk": national_comment.id, "count": user_comment.like_click_count})
    else:
        like = NationalCommentLikeIpAddress()
        like.ip = ip
        try:
            like.user = views.get_current_user(request)
        except:
            pass
        like.area = national_comment.country.area
        like.country = national_comment.country
        like.national_comment = national_comment
        like.comment_text = national_comment.text
        like.like_click_count += 1
        like.save()
        national_comment.like += 1
        national_comment.save()
        return JsonResponse({"like":national_comment.like, "pk": national_comment.id, "count": like.like_click_count})

# 【代表】コメント削除(※ログインユーザーのみ可能)
@login_required
def national_comment_remove(request, pk):
    national_comment = get_object_or_404(NationalComment, pk=pk)
    national_comment.delete()
    return redirect('soccer:national_detail', slug=national_comment.country.slug)


# 【代表】プロフィール更新リクエストフォーム
class NationalUpdateRequestFormView(CreateView):
    model = NationalUpdateRequest
    form_class = NationalUpdateRequestForm
    template_name = "request/national_team_update_request_form.html"

    def get_form_kwargs(self):
        kwargs = super(NationalUpdateRequestFormView,self).get_form_kwargs()
        kwargs['country_slug'] =self.kwargs['slug']
        return kwargs

    def national_team_update_request_save(self,form,slug):
        request = form.save(commit=False)
        obj = Country.objects.get(slug=slug)
        request.country_id = obj.id
        request.save()
        messages.success(self.request, 'プロフィールの更新リクエストが送信されました')
        return redirect('soccer:national_detail', slug=slug)
    
    def form_valid(self,form):
        subject = "【代表チーム】更新リクエストが届きました"
        form_name = form.cleaned_data['name']
        form_capital = form.cleaned_data['capital']
        form_area = form.cleaned_data['area']
        form_association = form.cleaned_data['association']
        message = F"""下記内容の代表チーム更新リクエストが届きました。

━━━　更新リクエストの内容　━━━

名前：{form_name}
首都：{form_capital}
地域：{form_area}
協会・連盟：{form_association}

━━━━━━━━━━━━━━━━━━

下記リンクより更新もしくは削除の対応を行ってください。
{settings.PROTOCOL}://{settings.DOMAIN}/{settings.DJANGO_ADMIN_URL}soccer/nationalupdaterequest/
"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_email)
        national_team_slug = self.kwargs['slug']
        return NationalUpdateRequestFormView.national_team_update_request_save(self,form,national_team_slug)


# 【代表】新規追加リクエストフォーム
class NationalNewCreateRequestFormView(CreateView):
    model = NationalNewCreateRequest
    form_class = NationalNewCreateRequestForm
    template_name = "request/national_team_new_create_request_form.html"

    def national_team_new_create_request_save(self,form):
        request = form.save(commit=False)
        request.user_ip_address = views.get_ip(self.request)
        request.save()
        # messages.success(self.request, '監督の新規追加リクエストが送信されました')
        return redirect('soccer:national_team_request_result')

    def form_valid(self,form):
        subject = "【代表チーム】新規追加リクエストが届きました"
        form_name = form.cleaned_data['name']
        form_capital = form.cleaned_data['capital']
        form_area = form.cleaned_data['area']
        form_association = form.cleaned_data['association']
        message = F"""下記内容の代表チーム追加リクエストが届きました。

━━━　新規追加リクエストの内容　━━━

名前：{form_name}
首都：{form_capital}
地域：{form_area}
協会・連盟：{form_association}

━━━━━━━━━━━━━━━━━━━━

下記リンクより新規追加もしくは削除の対応を行ってください。
{settings.PROTOCOL}://{settings.DOMAIN}/{settings.DJANGO_ADMIN_URL}soccer/nationalnewcreaterequest/
"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_email)
        return NationalNewCreateRequestFormView.national_team_new_create_request_save(self,form)
