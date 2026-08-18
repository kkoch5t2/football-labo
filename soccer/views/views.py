from django.views.generic.edit import CreateView, FormView 
from django.views.generic.list import ListView, MultipleObjectMixin 
from django.views.generic import TemplateView, DetailView

from django.db.models import Count, Avg, Q, Sum, F
from django.db.models.signals import post_save

from django.core.mail import send_mail
from django.core.paginator import Paginator

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordContextMixin, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator 
from django.contrib.sessions.models import Session
from django.contrib import messages

from django.conf import settings

from datetime import datetime, timedelta

from django.dispatch import receiver

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.urls import reverse_lazy

from django.template.loader import render_to_string

import re

from soccer.forms import(
    ContactForm,
    SignupForm,
    LoginForm,
    UserNameChangeForm,
    NickNameChangeForm,
    EmailChangeForm,
    UserIconChangeForm,
    PasswordChangeForm,
    CustomPasswordResetForm,
    SetPasswordForm,
    ProfileMessageChangeForm,
)

from soccer.models import(
    Player,
    Comment,
    LikeIpAddress,
    Manager,
    ManagerComment,
    ManagerLikeIpAddress,
    Team,
    ClubComment,
    ClubCommentLikeIpAddress,
    Country,
    NationalComment,
    NationalCommentLikeIpAddress,
    Contact,
    UserActivateTokens,
    CustomUser,
    Connection,
)


# 【選手】トップページ
class IndexView(ListView):
    template_name = 'soccer/index.html'
    model = Player
    paginate_by = 5

    queryset = Player.objects.annotate(
        num_comments=Count('comments')).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({
            'gk_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'GK').exclude(num_comments=0),
            'cb_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'CB').exclude(num_comments=0),
            'lb_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'LB').exclude(num_comments=0),
            'rb_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'RB').exclude(num_comments=0),
            'dm_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'DM').exclude(num_comments=0),
            'lwb_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'LWB').exclude(num_comments=0),
            'rwb_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'RWB').exclude(num_comments=0),
            'cm_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'CM').exclude(num_comments=0),
            'am_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'AM').exclude(num_comments=0),
            'lm_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'LM').exclude(num_comments=0),
            'rm_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'RM').exclude(num_comments=0),
            'ss_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'SS').exclude(num_comments=0),
            'lw_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'LW').exclude(num_comments=0),
            'rw_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'RW').exclude(num_comments=0),
            'cf_ranking_list':Player.objects.annotate(
                num_comments=Count('comments'), avg_ovr=Avg('comments__ovr'), like_count=Sum('comments__like'), average_total_ratings=(Sum('comments__shoot') + Sum('comments__dribble') + Sum('comments__pas') + Sum('comments__defense') + Sum('comments__physical') + Sum('comments__speed')) / Count('comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').filter(main_position = 'CF').exclude(num_comments=0),
            'manager_list': Manager.objects.annotate(
                num_comments=Count('manager_comments'), avg_ovr=Avg('manager_comments__ovr'), like_count=Sum('manager_comments__like'), average_total_ratings=(Sum('manager_comments__attack') + Sum('manager_comments__defense') + Sum('manager_comments__achievement') + Sum('manager_comments__management') + Sum('manager_comments__achievement') + Sum('manager_comments__political')) / Count('manager_comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').exclude(num_comments=0),
            'club_team_list': Team.objects.annotate(
                num_comments=Count('club_comments'), avg_ovr=Avg('club_comments__ovr'), like_count=Sum('club_comments__like'), average_total_ratings=(Sum('club_comments__attack') + Sum('club_comments__defense') + Sum('club_comments__manager') + Sum('club_comments__front') + Sum('club_comments__development')) / Count('club_comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').exclude(num_comments=0),
            'national_team_list': Country.objects.annotate(
                num_comments=Count('national_comments'), avg_ovr=Avg('national_comments__ovr'), like_count=Sum('national_comments__like'), average_total_ratings=(Sum('national_comments__attack') + Sum('national_comments__defense') + Sum('national_comments__manager') + Sum('national_comments__association') + Sum('national_comments__development')) / Count('national_comments')).order_by(F('avg_ovr').desc(nulls_last=True), '-num_comments', '-like_count', '-average_total_ratings', '-created_at').exclude(num_comments=0),
        })
        return context


# 【共通】IPアドレスを取得する機能
def get_ip(request):
    forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_addresses:
        ip = forwarded_addresses.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# 【選手・監督】リクエストフォーム
class RequestFormView(TemplateView):
    template_name = "request/request_menu.html"


# 【選手・監督】リクエスト送信完了
class RequestResultView(TemplateView):
    template_name = 'request/request_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = "リクエストは正常に送信されました。"
        return context


# お問い合わせフォーム
class ContactFormView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "contact/contact_form.html"
    success_url = "result/"

    def form_valid(self, form):
        # お問い合わせを行ったユーザーへの自動返信メールの設定
        subject = "【みんなのサッカーラボ】お問い合わせを受け付けいたしました"
        form_name = form.cleaned_data['name']
        form_email = form.cleaned_data['email']
        if form.cleaned_data['subject'] == None:
            form_subject = ""
        else:
            form_subject = "form.cleaned_data['subject']"
        form_inquiry_details = form.cleaned_data['inquiry_details']
        context = {
            'form_name':form_name,
            'form_email':form_email,
            'form_subject':form_subject,
            'form_inquiry_details':form_inquiry_details,
        }
        message = render_to_string("text_file/contact_form/contact_form_auto_send.txt", context)
        from_email = settings.CONTACT_EMAIL
        to_email = [form.cleaned_data['email']]
        send_mail(subject, message, from_email, to_email)
        
        # お問い合わせが届いたことをサイト管理者に通知するメールの設定
        subject_to_administrator = "【みんなのサッカーラボ】お問い合わせが届きました"
        message_to_administrator = render_to_string("text_file/contact_form/contact_form_receive_notification.txt", context)
        to_administrator_email = [settings.CONTACT_EMAIL]
        send_mail(subject_to_administrator, message_to_administrator, from_email, to_administrator_email)
        return super().form_valid(form)


# お問い合わせ送信完了
class ContactResultView(TemplateView):
    template_name = 'contact/contact_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = "お問い合わせは正常に送信されました。"
        return context


def activate_user(request, activate_token):
    activated_user = UserActivateTokens.objects.activate_user_by_token(
        activate_token
    )
    if hasattr(activated_user, 'is_active'):
        if activated_user.is_active:
            return render(request, 'text_file/user_activation/activation_finish.html')
        if not activated_user.is_active:
            message = 'アクティベーションが失敗しています。管理者に問い合わせてください'
    if not hasattr(activated_user, 'is_active'):
        message = 'エラーが発生しました'
    return HttpResponse(message)


# 新規ユーザー登録機能
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('soccer:user_player_comment_list', request.user.username)
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'user/signup_temporary_finish.html')
    else:
        form = SignupForm()
    param = {
        'form': form
    }
    return render(request, 'user/signup.html', param)


# 新規ユーザー登録の一時完了画面
def signup_temporary_finish_view(request):
    return render(request, 'user/signup_temporary_finish.html')


# ユーザーログイン
def login_view(request):
    try:
        login_user = get_current_user(request)
        if login_user:
            return HttpResponseRedirect(reverse_lazy('soccer:user_player_comment_list', kwargs={'username': login_user.username}))
    except:
        pass

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                login_user = CustomUser.objects.get(username=request.user.username)
                return HttpResponseRedirect(reverse_lazy('soccer:user_player_comment_list', kwargs={'username': login_user.username}))
        else:
            messages.error(request, 'ログインに失敗しました。')
    else:
        form = LoginForm()
    param = {
        'form': form,
    }
    return render(request, 'user/login.html', param)


# ユーザーログアウト
def logout_view(request):
    logout(request)
    return render(request, 'user/logout.html')


# ユーザー削除画面（HTML）の指定
class UserDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'user/user_delete.html'


# ユーザー削除前最終画面（HTML）の指定
class UserDeleteConfirmView(LoginRequiredMixin, TemplateView):
    template_name = 'user/user_delete_confirm.html'


# ユーザー削除
def user_delete_view(request):
    try:
        login_user = get_current_user(request)
        login_user.delete()
        return redirect('soccer:index')
    except:
        raise Http404


# メールアドレス認証のためのメール送信
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def publish_activate_token(sender, instance, **kwargs):
    from_email = settings.DEFAULT_FROM_EMAIL
    user_activate_token = UserActivateTokens.objects.create(
            user=instance,
            expired_at=datetime.now()+timedelta(days=settings.ACTIVATION_EXPIRED_DAYS),
        )
    if not instance.is_active:
        context = {
            'username':user_activate_token.user.username,
            'activate_token':user_activate_token.activate_token,
            'protocol':settings.PROTOCOL,
            'domain':settings.DOMAIN,
        }
        subject = '【みんなのサッカーラボ】メールアドレスの認証'
        message = render_to_string("text_file/user_activation/activation_mail.txt", context)
        recipient_list = [
            instance.email,
        ]
        send_mail(subject, message, from_email, recipient_list)


# フォローリスト
class FollowingListView(ListView):
    template_name = 'user/following_list.html'
    model = Connection
    paginate_by = 20
    queryset = Connection.objects.order_by('-date_created')

    def get_queryset(self):
        username = self.kwargs['username']
        self.user = get_object_or_404(CustomUser, username=username)
        qs = super().get_queryset().filter(follower=self.user)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        return context


# フォロワーリスト
class FollowerListView(ListView):
    template_name = 'user/follower_list.html'
    model = Connection
    paginate_by = 20
    queryset = Connection.objects.order_by('-date_created')

    def get_queryset(self):
        username = self.kwargs['username']
        self.user = get_object_or_404(CustomUser, username=username)
        qs = super().get_queryset().filter(following=self.user)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        return context


# ユーザーのフォロー
@login_required
def follow_view(request, *args, **kwargs):
    try:
        #request.user.username = ログインユーザーのユーザー名を渡す。
        follower = CustomUser.objects.get(username=request.user.username)
        #kwargs['username'] = フォロー対象のユーザー名を渡す。
        following = CustomUser.objects.get(username=kwargs['username'])
    #例外処理：もしフォロー対象が存在しない場合、警告文を表示させる。
    except CustomUser.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['username'])) #（※1）（※2）
        return HttpResponseRedirect(reverse_lazy('soccer:index'))
    #フォローしようとしている対象が自分の場合、警告文を表示させる。
    if follower == following:
        messages.warning(request, '自分自身はフォローできません')
    else:
        #フォロー対象をまだフォローしていなければ、DBにフォロワー(自分)×フォロー(相手)という組み合わせで登録する。
        #createdにはTrueが入る
        _, created = Connection.objects.get_or_create(follower=follower, following=following) #（※3）

        #もしcreatedがTrueの場合、フォロー完了のメッセージを表示させる。
        if (created):
            messages.success(request, '{}をフォローしました'.format(following.username))
        #既にフォロー相手をフォローしていた場合、createdにはFalseが入る。
        #フォロー済みのメッセージを表示させる。
        else:
            messages.warning(request, 'すでに{}をフォローしています'.format(following.username))

    return HttpResponseRedirect(reverse_lazy('soccer:user_player_comment_list', kwargs={'username': following.username}))


# ユーザーのフォロー解除
@login_required
def unfollow_view(request, *args, **kwargs):
    try:
        follower = CustomUser.objects.get(username=request.user.username)
        following = CustomUser.objects.get(username=kwargs['username'])
        if follower == following:
            messages.warning(request, '自分自身のフォローを外せません')
        else:
            unfollow = Connection.objects.get(follower=follower, following=following)
            #フォロワー(自分)×フォロー(相手)という組み合わせを削除する。
            unfollow.delete()
            messages.success(request, '{}のフォローを外しました'.format(following.username))
    except CustomUser.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['username']))
        return HttpResponseRedirect(reverse_lazy('soccer:index'))
    except Connection.DoesNotExist:
        messages.warning(request, '{0}をフォローしませんでした'.format(following.username))

    return HttpResponseRedirect(reverse_lazy('soccer:user_player_comment_list', kwargs={'username': following.username}))


# セッションをもとにユーザーを返す関数
def get_current_user(request=None):
    try:
        if not request:
            return None
        session_key = request.session.session_key
        session = Session.objects.get(session_key=session_key).get_decoded()
        uid = session.get('_auth_user_id')
        return CustomUser.objects.get(id=uid)
    except:
        raise Http404


# ユーザー詳細画面（選手コメント用）
class UserProifilePlayerCommentDetail(MultipleObjectMixin, DetailView):
    model = CustomUser
    paginate_by = 10

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        request_user = CustomUser.objects.get(username=username)
        object_list = Comment.objects.filter(user=request_user).order_by('-timestamp')
        context = super(UserProifilePlayerCommentDetail, self).get_context_data(object_list=object_list, **kwargs)
        context['username'] = username
        context['request_user'] = request_user
        if self.request.user.is_authenticated:
            context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()

        try:
            if username is not context['user'].username:
                result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
                context['connected'] = True if result else False
        except:
            context['connected'] = False
        return context


# ユーザー詳細画面（監督コメント用）
class UserProifileManagerCommentDetail(MultipleObjectMixin, DetailView):
    model = CustomUser
    paginate_by = 10

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        request_user = CustomUser.objects.get(username=username)
        object_list = ManagerComment.objects.filter(user=request_user).order_by('-timestamp')
        context = super(UserProifileManagerCommentDetail, self).get_context_data(object_list=object_list, **kwargs)
        context['username'] = username
        context['request_user'] = request_user
        if self.request.user.is_authenticated:
            context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()
        
        try:
            if username is not context['user'].username:
                result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
                context['connected'] = True if result else False
        except:
            context['connected'] = False
        return context


# ユーザー詳細画面（クラブコメント用）
class UserProifileClubCommentDetail(MultipleObjectMixin, DetailView):
    model = CustomUser
    paginate_by = 10

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        request_user = CustomUser.objects.get(username=username)
        object_list = ClubComment.objects.filter(user=request_user).order_by('-timestamp')
        context = super(UserProifileClubCommentDetail, self).get_context_data(object_list=object_list, **kwargs)
        context['username'] = username
        context['request_user'] = request_user
        if self.request.user.is_authenticated:
            context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()
        
        try:
            if username is not context['user'].username:
                result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
                context['connected'] = True if result else False
        except:
            context['connected'] = False
        return context


# ユーザー詳細画面（代表コメント用）
class UserProifileNationalCommentDetail(MultipleObjectMixin, DetailView):
    model = CustomUser
    paginate_by = 10

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        request_user = CustomUser.objects.get(username=username)
        object_list = NationalComment.objects.filter(user=request_user).order_by('-timestamp')
        context = super(UserProifileNationalCommentDetail, self).get_context_data(object_list=object_list, **kwargs)
        context['username'] = username
        context['request_user'] = request_user
        if self.request.user.is_authenticated:
            context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()
        
        try:
            if username is not context['user'].username:
                result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
                context['connected'] = True if result else False
        except:
            context['connected'] = False
        return context


# ユーザー詳細画面（いいね選手コメント用）
class UserProifilePlayerLikeDetail(MultipleObjectMixin, DetailView):
    model = CustomUser
    paginate_by = 10

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        request_user = CustomUser.objects.get(username=username)
        object_list = LikeIpAddress.objects.filter(user=request_user, like_flg='1').order_by('-updated_at')
        context = super(UserProifilePlayerLikeDetail, self).get_context_data(object_list=object_list, **kwargs)
        context['username'] = username
        context['request_user'] = request_user
        if self.request.user.is_authenticated:
            context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()
        
        try:
            if username is not context['user'].username:
                result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
                context['connected'] = True if result else False
        except:
            context['connected'] = False
        return context


# ユーザー詳細画面（いいねした監督コメント用）
class UserProifileManagerLikeDetail(MultipleObjectMixin, DetailView):
    model = CustomUser
    paginate_by = 10

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        request_user = CustomUser.objects.get(username=username)
        object_list = ManagerLikeIpAddress.objects.filter(user=request_user, like_flg='1').order_by('-updated_at')
        context = super(UserProifileManagerLikeDetail, self).get_context_data(object_list=object_list, **kwargs)
        context['username'] = username
        context['request_user'] = request_user
        if self.request.user.is_authenticated:
            context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()
        
        try:
            if username is not context['user'].username:
                result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
                context['connected'] = True if result else False
        except:
            context['connected'] = False
        return context


# ユーザー詳細画面（いいねしたクラブコメント用）
class UserProifileClubLikeDetail(MultipleObjectMixin, DetailView):
    model = CustomUser
    paginate_by = 10

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        request_user = CustomUser.objects.get(username=username)
        object_list = ClubCommentLikeIpAddress.objects.filter(user=request_user, like_flg='1').order_by('-updated_at')
        context = super(UserProifileClubLikeDetail, self).get_context_data(object_list=object_list, **kwargs)
        context['username'] = username
        context['request_user'] = request_user
        if self.request.user.is_authenticated:
            context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()
        
        try:
            if username is not context['user'].username:
                result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
                context['connected'] = True if result else False
        except:
            context['connected'] = False
        return context


# ユーザー詳細画面（いいねした代表コメント用）
class UserProifileNationalLikeDetail(MultipleObjectMixin, DetailView):
    model = CustomUser
    paginate_by = 10

    #slug_field = urls.pyに渡すモデルのフィールド名
    slug_field = 'username'
    # urls.pyでのキーワードの名前
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        request_user = CustomUser.objects.get(username=username)
        object_list = NationalCommentLikeIpAddress.objects.filter(user=request_user, like_flg='1').order_by('-updated_at')
        context = super(UserProifileNationalLikeDetail, self).get_context_data(object_list=object_list, **kwargs)
        context['username'] = username
        context['request_user'] = request_user
        if self.request.user.is_authenticated:
            context['user'] = get_current_user(self.request)
        context['following'] = Connection.objects.filter(follower__username=username).count()
        context['follower'] = Connection.objects.filter(following__username=username).count()
        
        try:
            if username is not context['user'].username:
                result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
                context['connected'] = True if result else False
        except:
            context['connected'] = False
        return context


# パスワード変更
class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'registration/password_change_form.html'


# パスワード変更完了
class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    template_name = 'registration/password_change_done.html'


# パスワードリセット（ログイン前）
class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    # subject_template_name = 'user/mail_template/reset/subject.txt'
    # email_template_name = 'user/mail_template/reset/message.txt'
    email_template_name = 'user/password_reset_email.html'
    template_name = 'user/password_reset_form.html'
    success_url = reverse_lazy('soccer:password_reset_done')
    form_class = CustomPasswordResetForm


# パスワードリセット（ログイン前）のメール送信完了
class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'user/password_reset_done.html'


# パスワードリセットメール認証後の新規パスワード入力
class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    success_url = reverse_lazy('soccer:password_reset_complete')
    template_name = 'user/password_reset_confirm.html'
    form_class = SetPasswordForm


# パスワードリセットメール認証後の新規パスワード入力完了
class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'user/password_reset_complete.html'


# ニックネーム変更
class NickNameChangeView(LoginRequiredMixin, FormView):
    template_name = 'registration/change.html'
    form_class = NickNameChangeForm

    def form_valid(self, form):
        #formのupdateメソッドにログインユーザーを渡して更新
        form.update(user=self.request.user)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 更新前のユーザー情報をkwargsとして渡す
        kwargs.update({
            'nickname' : self.request.user.nickname,
        })
        return kwargs


# ニックネーム変更完了
class NickNameChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/change_done.html'


# ユーザー名変更
class UserNameChangeView(LoginRequiredMixin, FormView):
    template_name = 'registration/change.html'
    form_class = UserNameChangeForm

    def form_valid(self, form):
        #formのupdateメソッドにログインユーザーを渡して更新
        form.update(user=self.request.user)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 更新前のユーザー情報をkwargsとして渡す
        kwargs.update({
            'username' : self.request.user.username,
        })
        return kwargs


# ユーザー名変更完了
class UserNameChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/change_done.html'


# メールアドレス変更
class EmailChangeView(LoginRequiredMixin, FormView):
    template_name = 'registration/change.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        #formのupdateメソッドにログインユーザーを渡して更新
        change_email_form = form.save(commit=False)
        try:
            same_email_user = CustomUser.objects.get(email=change_email_form.change_email)
        except CustomUser.DoesNotExist:
            same_email_user = None
        if same_email_user is None:
            form.update(user=self.request.user)
            email_change_form = form.save(commit=False)
            user_activate_token = UserActivateTokens.objects.create(
                user=self.request.user,
                expired_at=datetime.now()+timedelta(days=settings.ACTIVATION_EXPIRED_DAYS),
            )
            context = {
                'username':user_activate_token.user.username,
                'activate_token':user_activate_token.activate_token,
                'protocol':settings.PROTOCOL,
                'domain':settings.DOMAIN,
            }
            subject = '【みんなのサッカーラボ】メールアドレス変更'
            message = render_to_string("text_file/user_activation/activation_change_email.txt", context)
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [
                email_change_form.change_email,
            ]
            send_mail(subject, message, from_email, recipient_list)
            return super().form_valid(form)
        else:
            messages.error(self.request, 'すでに登録されているメールアドレスです')
            return redirect('soccer:email_change_form')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 更新前のユーザー情報をkwargsとして渡す
        kwargs.update({
            'email' : self.request.user.email,
        })
        return kwargs


# メールアドレス変更完了
class EmailChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/change_done.html'


# メールアドレス変更のためのメールアドレス認証でアクティベーション用のURLが叩かれたらHTTPResponseを返す
def change_email(request, activate_token):
    activated_user = UserActivateTokens.objects.activate_user_by_token(
        activate_token
    )
    if activated_user.change_email is not None:
        activated_user.email = activated_user.change_email
        activated_user.change_email = None
        activated_user.save()
        return render(request, 'text_file/user_activation/activation_finish.html')
    else:
        message = 'エラーが発生しました'
    return HttpResponse(message)


# ユーザーアイコン変更
class UserIconChangeView(LoginRequiredMixin, FormView):
    template_name = 'user/user_icon_change.html'
    form_class = UserIconChangeForm

    def form_valid(self, form):
        # formのupdateメソッドにログインユーザーを渡して更新
        form.update(user=self.request.user, request=self.request.FILES)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_current_user(self.request)
        return context


# ユーザーアイコン変更完了
class UserIconChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'user/user_icon_change_finish.html'


# 自己紹介文変更
class ProfileMessageChangeView(LoginRequiredMixin, FormView):
    template_name = 'user/profile_message_change_form.html'
    form_class = ProfileMessageChangeForm

    def form_valid(self, form):
        # formのupdateメソッドにログインユーザーを渡して更新
        form.update(user=self.request.user, request=self.request.user.profile_message)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 更新前のユーザー情報をkwargsとして渡す
        kwargs.update({
            'profile_message' : self.request.user.profile_message,
        })
        return kwargs


# 自己紹介文変更完了
class ProfileMessageDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile_message_change_finish.html'


# ユーザー設定
class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'user/user_settings.html'


# ユーザー一覧
class UserListView(ListView):
    model = CustomUser
    template_name = 'user/user_list.html'
    paginate_by = 10

    queryset = CustomUser.objects.filter(is_active=True).order_by('-date_joined')

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        lookups = (
            Q(username__icontains=query)|
            Q(nickname__icontains=query) 
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


def get_queryset_user_timeline_comment(request):
    login_user = get_current_user(request)
    following_users = Connection.objects.filter(follower__username=login_user.username)
    users_list = []
    users_list.append(login_user.username)
    for i in range(len(following_users)):
        following_user = str(following_users[i])
        target = ' : '
        idx = following_user.find(target)
        following_user_name = following_user[idx+len(target):]
        users_list.append(following_user_name)
    return users_list


# フォロー中のユーザーの選手コメント投稿一覧
class UserTimeLinePlayerCommentView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name='user/user_timeline/user_timeline_player_comment.html'
    paginate_by = 10
    queryset = Comment.objects.order_by('-timestamp')

    def get_queryset(self):
        try:
            users_list = get_queryset_user_timeline_comment(self.request)
            qs = super().get_queryset().filter(user__username__in=users_list)
            return qs
        except:
            raise Http404
        

# フォロー中のユーザーの監督コメント投稿一覧
class UserTimeLineManagerCommentView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name='user/user_timeline/user_timeline_manager_comment.html'
    paginate_by = 10
    queryset = ManagerComment.objects.order_by('-timestamp')

    def get_queryset(self):
        try:
            users_list = get_queryset_user_timeline_comment(self.request)
            qs = super().get_queryset().filter(user__username__in=users_list)
            return qs
        except:
            raise Http404


# フォロー中のユーザーのクラブコメント投稿一覧
class UserTimeLineClubCommentView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name='user/user_timeline/user_timeline_club_comment.html'
    paginate_by = 10
    queryset = ClubComment.objects.order_by('-timestamp')

    def get_queryset(self):
        try:
            users_list = get_queryset_user_timeline_comment(self.request)
            qs = super().get_queryset().filter(user__username__in=users_list)
            return qs
        except:
            raise Http404
        

# フォロー中のユーザーの選手コメント投稿一覧
class UserTimeLineNationalCommentView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name='user/user_timeline/user_timeline_national_comment.html'
    paginate_by = 10
    queryset = NationalComment.objects.order_by('-timestamp')

    def get_queryset(self):
        try:
            users_list = get_queryset_user_timeline_comment(self.request)
            qs = super().get_queryset().filter(user__username__in=users_list)
            return qs
        except:
            raise Http404
