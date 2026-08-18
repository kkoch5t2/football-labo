from django import forms
from django.shortcuts import get_object_or_404
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from myproject.settings import RECAPTCHA_PUBLIC_KEY, RECAPTCHA_PRIVATE_KEY

from django.forms import TextInput, Textarea, NumberInput, EmailInput, PasswordInput, FileInput

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

UserModel = get_user_model()

from soccer.models import(
    Player,
    Comment,
    Manager,
    ManagerComment,
    Country,
    NationalComment,
    Team,
    ClubComment,
    PlayerUpdateRequest,
    ManagerUpdateRequest,
    ClubUpdateRequest, 
    NationalUpdateRequest,
    PlayerNewCreateRequest,
    ManagerNewCreateRequest,
    ClubNewCreateRequest, 
    NationalNewCreateRequest, 
    Contact,
    POSITION_CHOICES,
    DOMINANT_FOOT_CHOICES,
    CustomUser,
)


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if self.user.is_authenticated:
            self.fields['author'].initial = self.user.nickname
            self.fields['author'].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = Comment
        fields = (
            'author',
            'ovr',
            'shoot',
            'dribble',
            'pas',
            'defense',
            'physical',
            'speed',
            'saving',
            'handling',
            'kick',
            'positioning',
            'reflexes',
            'text'
        )
        widgets = {
            'author': TextInput(attrs={
                'class': 'form-control',
            }),
            'ovr': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'shoot': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'dribble': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'pas': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'defense': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'physical': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'speed': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'saving': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'handling': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'kick': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'positioning': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'reflexes': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'text': Textarea(attrs={
                'class': 'form-control',
            }),
        }


class ManagerCommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if self.user.is_authenticated:
            self.fields['author'].initial = self.user.nickname
            self.fields['author'].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = ManagerComment
        fields = ('author', 'ovr', 'attack', 'defense', 'achievement', 'management', 'development', 'political', 'text')
        widgets = {
            'author': TextInput(attrs={
                'class': 'form-control',
            }),

            'ovr': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'attack': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'defense': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'achievement': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'management': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'development': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'political': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'text': Textarea(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'author' : '名前',
            'ovr' : '総合評価',
            'attack': '攻撃戦術の評価',
            'defense' : '守備戦術の評価',
            'achievement' : '実績の評価',
            'management' : 'マネジメントの評価',
            'development' : '育成力の評価',
            'political' : '政治力の評価',
            'text' : 'コメント（700字まで）',
        }


class ClubCommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if self.user.is_authenticated:
            self.fields['author'].initial = self.user.nickname
            self.fields['author'].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = ClubComment
        fields = ('author', 'ovr', 'attack', 'defense', 'manager', 'front', 'development', 'text')
        widgets = {
            'author': TextInput(attrs={
                'class': 'form-control',
            }),

            'ovr': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'attack': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'defense': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'manager': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'front': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'development': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'money': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'text': Textarea(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'author' : '名前',
            'ovr' : '総合評価',
            'attack': '攻撃力の評価',
            'defense' : '守備力の評価',
            'manager' : '監督・コーチの評価',
            'front' : 'フロントの評価',
            'development' : '育成力の評価',
            'text' : 'コメント（700字まで）',
        }


class NationalCommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if self.user.is_authenticated:
            self.fields['author'].initial = self.user.nickname
            self.fields['author'].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = NationalComment
        fields = ('author', 'ovr', 'attack', 'defense', 'manager', 'association', 'development', 'text')
        widgets = {
            'author': TextInput(attrs={
                'class': 'form-control',
            }),

            'ovr': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'attack': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'defense': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'manager': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'association': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'development': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),

            'text': Textarea(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'author' : '名前',
            'ovr' : '総合評価',
            'attack': '攻撃力の評価',
            'defense' : '守備力の評価',
            'manager' : '監督・コーチの評価',
            'association': '協会・連盟の評価',
            'development' : '育成力の評価',
            'text' : 'コメント（700字まで）',
        }


class ManagerUpdateRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.manager_id  = kwargs.pop('manager_id')
        obj = Manager.objects.get(pk=self.manager_id)
        super(ManagerUpdateRequestForm, self).__init__(*args, **kwargs)
        self.fields['league'].initial = obj.league
        self.fields['team'].initial = obj.team
        self.fields['area'].initial = obj.area
        self.fields['country'].initial = obj.country
        self.fields['name'].initial = obj.name
        self.fields['birthday'].initial = obj.birthday
        
    class Meta:
        model = ManagerUpdateRequest
        fields = ('league', 'team', 'area', 'country', 'name', 'birthday')
        widgets = {
            'league': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'team': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'area': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'country': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'birthday': TextInput(attrs={
                'class': 'custom-select md-form',
                'type': 'date',
            }),
        }
        labels = {
            'manager_id' : '監督ID',
            'league' : '所属リーグ',
            'team': '所属チーム',
            'area' : '出身地域',
            'country' : '出身国',
            'name' : '名前',
            'birthday' : '生年月日',
        }
        
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class PlayerUpdateRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.player_id  = kwargs.pop('player_id')
        obj = Player.objects.get(pk=self.player_id)
        super(PlayerUpdateRequestForm, self).__init__(*args, **kwargs)
        self.fields['league'].initial = obj.league
        self.fields['team'].initial = obj.team
        self.fields['area'].initial = obj.area
        self.fields['country'].initial = obj.country
        self.fields['name'].initial = obj.name
        self.fields['birthday'].initial = obj.birthday
        self.fields['height'].initial = obj.height
        self.fields['foot'].initial = obj.foot
        self.fields['main_position'].initial = obj.main_position
        self.fields['second_position'].initial = obj.second_position
        self.fields['third_position'].initial = obj.third_position

    class Meta:
        model = PlayerUpdateRequest
        fields = ('league', 'team', 'area', 'country', 'name', 'birthday', 'height', 'foot', 'main_position', 'second_position', 'third_position')
        widgets = {
            'league': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'team': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'area': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'country': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'birthday': TextInput(attrs={
                'class': 'custom-select md-form',
                'type': 'date',
            }),
            'height': NumberInput(attrs={
                'class': 'form-control',
            }),
            'foot': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'main_position': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'second_position': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'third_position': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
        }
        
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class ClubUpdateRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.team_slug  = kwargs.pop('team_slug')
        obj = Team.objects.get(slug=self.team_slug)
        super(ClubUpdateRequestForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = obj.name
        self.fields['year_established'].initial = obj.year_established
        self.fields['home_town'].initial = obj.home_town
        self.fields['league'].initial = obj.league
        
    class Meta:
        model = ClubUpdateRequest
        fields = ('name', 'year_established', 'home_town', 'league')
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'year_established': NumberInput(attrs={
                'class': 'form-control',
            }),
            'home_town': TextInput(attrs={
                'class': 'form-control',
            }),
            'league': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
        }
        
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class NationalUpdateRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.country_slug  = kwargs.pop('country_slug')
        obj = Country.objects.get(slug=self.country_slug)
        super(NationalUpdateRequestForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = obj.name
        self.fields['capital'].initial = obj.capital
        self.fields['area'].initial = obj.area
        self.fields['association'].initial = obj.association

    class Meta:
        model = NationalUpdateRequest
        fields = ('name', 'capital', 'area', 'association')
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'capital': TextInput(attrs={
                'class': 'form-control',
            }),
            'area': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'association': TextInput(attrs={
                'class': 'form-control',
            }),
        }
        
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class ManagerNewCreateRequestForm(forms.ModelForm):
    class Meta:
        model = ManagerNewCreateRequest
        fields = (
            'league',
            'team',
            'area',
            'country',
            'name',
            'birthday',
            'author',
            'ovr',
            'attack_rating',
            'defense_rating',
            'achievement_rating',
            'management_rating',
            'development_rating',
            'political_rating',
            'comment_text'
        )
        widgets = {
            'league': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'team': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'area': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'country': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'birthday': TextInput(attrs={
                'class': 'custom-select md-form',
                'type': 'date',
            }),
            'author': TextInput(attrs={
                'class': 'form-control',
            }),
            'ovr': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'attack_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'defense_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'achievement_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'management_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'development_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'political_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'comment_text': Textarea(attrs={
                'class': 'form-control',
            }),
        }
        
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class PlayerNewCreateRequestForm(forms.ModelForm):
    class Meta:
        model = PlayerNewCreateRequest
        fields = (
            'league',
            'team',
            'area',
            'country',
            'name',
            'birthday',
            'height',
            'foot',
            'main_position',
            'second_position',
            'third_position',
            'author',
            'ovr',
            'shoot_rating',
            'dribble_rating',
            'pass_rating',
            'defense_rating',
            'physical_rating',
            'speed_rating',
            'comment_text'
        )
        widgets = {
            'league': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'team': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'area': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'country': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'birthday': TextInput(attrs={
                'class': 'custom-select md-form',
                'type': 'date',
            }),
            'height': NumberInput(attrs={
                'class': 'form-control',
            }),
            'foot': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'main_position': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'second_position': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'third_position': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'author': TextInput(attrs={
                'class': 'form-control',
            }),
            'ovr': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'shoot_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'dribble_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'pass_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'defense_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'physical_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'speed_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'comment_text': Textarea(attrs={
                'class': 'form-control',
            }),
        }
        
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class ClubNewCreateRequestForm(forms.ModelForm):
    class Meta:
        model = ClubNewCreateRequest
        fields = (
            'name',
            'league',
            'year_established',
            'home_town',
            'author',
            'ovr',
            'attack_rating',
            'defense_rating',
            'manager_rating',
            'front_rating',
            'development_rating',
            'comment_text'
        )
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'league': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'year_established': NumberInput(attrs={
                'class': 'form-control',
            }),
            'home_town': TextInput(attrs={
                'class': 'form-control',
            }),
            'author': TextInput(attrs={
                'class': 'form-control',
            }),
            'ovr': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'attack_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'defense_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'manager_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'front_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'development_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'comment_text': Textarea(attrs={
                'class': 'form-control',
            }),
        }

    captcha = ReCaptchaField(widget=ReCaptchaV3())


class NationalNewCreateRequestForm(forms.ModelForm):
    class Meta:
        model = NationalNewCreateRequest
        fields = (
            'name',
            'area',
            'capital',
            'association',
            'author',
            'ovr',
            'attack_rating',
            'defense_rating',
            'manager_rating',
            'association_rating',
            'development_rating',
            'comment_text'
        )
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'area': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'capital': TextInput(attrs={
                'class': 'form-control',
            }),
            'association': TextInput(attrs={
                'class': 'form-control',
            }),
            'author': TextInput(attrs={
                'class': 'form-control',
            }),
            'ovr': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'attack_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'defense_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'manager_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'association_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'development_rating': forms.Select(attrs={
                'class': 'custom-select md-form',
            }),
            'comment_text': Textarea(attrs={
                'class': 'form-control',
            }),
        }
        
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'inquiry_details')
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
            }),
            'subject': TextInput(attrs={
                'class': 'form-control',
            }),
            'inquiry_details': Textarea(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'name': '',
            'email': '',
            'subject': '',
            'inquiry_details': '',
        }

    captcha = ReCaptchaField(widget=ReCaptchaV3())


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = PasswordInput(attrs={'class': 'form-control'})

    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'email', 'password1', 'password2']
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'pattern': '^[A-Za-z0-9_]+$',
            }),
            'nickname': TextInput(attrs={
                'class': 'form-control',
            }),
            'email': EmailInput(attrs={
                'class': 'form-control',
            }),
        }
    
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = TextInput(attrs={'class': 'form-control'})
        self.fields['password'].widget = PasswordInput(attrs={'class': 'form-control'})
    
    captcha = ReCaptchaField(widget=ReCaptchaV3())


class UserNameChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
        ]
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control',
                'pattern': '^[A-Za-z0-9_]+$',
            }),
        }

    def __init__(self, username=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = TextInput(attrs={'class': 'form-control', 'pattern': '^[A-Za-z0-9_]+$'})
        # ユーザーの更新前情報をフォームに挿入
        if username:
            self.fields['username'].widget.attrs['value'] = username
        
    def update(self, user):
        user.username = self.cleaned_data['username']
        user.save()


class NickNameChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'nickname',
        ]

    def __init__(self, nickname=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields['nickname'].widget = TextInput(attrs={'class': 'form-control'})
        # ユーザーの更新前情報をフォームに挿入
        if nickname:
            self.fields['nickname'].widget.attrs['value'] = nickname
        
    def update(self, user):
        user.nickname = self.cleaned_data['nickname']
        user.save()


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'change_email',
        ]

    def __init__(self, email=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.fields['change_email'].widget = EmailInput(attrs={'class': 'form-control'})
        # ユーザーの更新前情報をフォームに挿入
        if email:
            self.fields['change_email'].widget.attrs['value'] = email

    def update(self, user):
        user.change_email = self.cleaned_data['change_email']
        user.save()


class PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = PasswordInput(attrs={'class': 'form-control'})
        self.fields['new_password1'].widget = PasswordInput(attrs={'class': 'form-control'})
        self.fields['new_password2'].widget = PasswordInput(attrs={'class': 'form-control'})


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = EmailInput(attrs={'class': 'form-control'})

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                'email': user_email,
                'domain': getattr(settings, "DOMAIN", None),
                'site_name': "みんなのサッカーラボ",
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                user_email, html_email_template_name=html_email_template_name,
            )


class SetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget = PasswordInput(attrs={'class': 'form-control'})
        self.fields['new_password2'].widget = PasswordInput(attrs={'class': 'form-control'})


class UserIconChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'user_icon',
        ]
        widgets = {
            'user_icon': FileInput(attrs={
                'type': 'file',
                'class': 'profile_image_input',
                'accept': 'image/*'
            }),
        }

    def __init__(self, user_icon=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        # ユーザーの更新前情報をフォームに挿入
        if user_icon:
            self.fields['user_icon'].widget.attrs['value'] = user_icon
        
    def update(self, user, request):
        user.user_icon.delete()
        user.user_icon = self.cleaned_data['user_icon']
        user.save()


class ProfileMessageChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'profile_message',
        ]
        widgets = {
            'profile_message': Textarea(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, profile_message=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        # ユーザーの更新前情報をフォームに挿入
        if profile_message:
            self.fields['profile_message'].initial = profile_message

    def update(self, user, request):
        user.profile_message = self.cleaned_data['profile_message']
        user.save()
        