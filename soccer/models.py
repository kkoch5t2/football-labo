from django.db import models
from django.db.models import Avg
# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid
from myproject.settings import base
from datetime import datetime


OVR_CHOICES = (
    (1, ' 1（最悪）'),
    (2, ' 2（悪い）'),
    (3, ' 3（少し悪い）'),
    (4, ' 4（普通）'),
    (5, ' 5（やや良い）'),
    (6, ' 6（良い）'),
    (7, ' 7（最高）'),
)


SCORE_CHOICES = (
    (None, '不明・評価しない'),
    (1, ' 1（最悪）'),
    (2, ' 2（悪い）'),
    (3, ' 3（少し悪い）'),
    (4, ' 4（普通）'),
    (5, ' 5（やや良い）'),
    (6, ' 6（良い）'),
    (7, ' 7（最高）'),
)


POSITION_CHOICES = (
    ('GK', 'GK（ゴールキーパー）'),
    ('CB', 'CB（センターバック）'),
    ('LB', 'LB（レフトバック）'),
    ('RB', 'RB（ライトバック）'),
    ('DM', 'DM（ディフェンシブミットフィルダー）'),
    ('LWB', 'LWB（レフトウイングバック）'),
    ('RWB', 'RWB（ライトウイングバック）'),
    ('CM', 'CM（セントラルミットフィルダー）'),
    ('AM', 'AM（アタッキングミットフィルダー）'),
    ('LM', 'LM（レフトミットフィルダー）'),
    ('RM', 'RM（ライトミットフィルダー）'),
    ('SS', 'SS（セカンドストライカー）'),
    ('LW', 'LW（レフトウインガー）'),
    ('RW', 'RW（ライトウインガー）'),
    ('CF', 'CF（センターフォワード）'),
)


DOMINANT_FOOT_CHOICES = (
    ('右足', '右足'),
    ('左足', '左足'),
)


LIKE_STATE_CHOICES = (
    ('0', '取り消し'),
    ('1', 'いいね済み'),
)


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    change_email = models.EmailField(max_length=100, blank=True, null=True)
    user_icon = models.ImageField(upload_to='user_icon/', null=True, blank=True)
    profile_message = models.TextField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    REQUIRED_FIELDS = ["email","is_active"]


class UserActivateTokensManager(models.Manager):
    def activate_user_by_token(self, activate_token):
        user_activate_token = self.filter(
            activate_token=activate_token,
            expired_at__gte=datetime.now() # __gte = greater than equal
        ).first()
        if hasattr(user_activate_token, 'user'):
            user = user_activate_token.user
            user.is_active = True
            user.save()
            return user


class UserActivateTokens(models.Model):
    token_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activate_token = models.UUIDField(default=uuid.uuid4)
    expired_at = models.DateTimeField()
    objects = UserActivateTokensManager()


class Connection(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='follower', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} : {}".format(self.follower.username, self.following.username)


class League(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    flag = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'リーグマスタ'
    
    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    year_established = models.IntegerField()
    home_town = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='team_logo/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'チームマスタ'

    def __str__(self):
        return self.name

    def avg_ratings(self):
        rating_average = self.club_comments.aggregate(
            Avg('ovr'),
            Avg('attack'),
            Avg('defense'),
            Avg('manager'),
            Avg('front'),
            Avg('development'),
        )
        return rating_average
    

class ClubComment(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='club_comments')
    author = models.CharField(max_length=30, default='匿名')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    ovr = models.PositiveSmallIntegerField(verbose_name='総合評価', null=True, default=4, choices=OVR_CHOICES)
    attack = models.PositiveSmallIntegerField(verbose_name='攻撃力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    defense = models.PositiveSmallIntegerField(verbose_name='守備力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    manager = models.PositiveSmallIntegerField(verbose_name='監督・コーチ', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    front = models.PositiveSmallIntegerField(verbose_name='フロント', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    development = models.PositiveSmallIntegerField(verbose_name='育成', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    text = models.TextField(max_length=700, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_ip_address = models.GenericIPAddressField(null=True)
    like = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'コメント（クラブ詳細）'
        
    def __str__(self):
        return self.author


class ClubCommentLikeIpAddress(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    club_comment = models.ForeignKey(ClubComment, on_delete=models.CASCADE)
    comment_text = models.TextField(max_length=700, null=True, blank=True)
    ip = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    like_flg = models.CharField(max_length=50, default='1', choices=LIKE_STATE_CHOICES)
    like_click_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name_plural = 'いいね・IPアドレス（クラブ詳細）'


class Area(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = '地域マスタ'

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    flag = models.TextField(blank=True, null=True)
    capital = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    association = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name_plural = '国籍マスタ'

    def __str__(self):
        return self.name

    def avg_ratings(self):
        rating_average = self.national_comments.aggregate(
            Avg('ovr'),
            Avg('attack'),
            Avg('defense'),
            Avg('manager'),
            Avg('association'),
            Avg('development'),
        )
        return rating_average
    

class NationalComment(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='national_comments')
    author = models.CharField(max_length=30, default='匿名')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    ovr = models.PositiveSmallIntegerField(verbose_name='総合評価', null=True, default=4, choices=OVR_CHOICES)
    attack = models.PositiveSmallIntegerField(verbose_name='攻撃力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    defense = models.PositiveSmallIntegerField(verbose_name='守備力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    manager = models.PositiveSmallIntegerField(verbose_name='監督・コーチ', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    association = models.PositiveSmallIntegerField(verbose_name='協会・連盟', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    development = models.PositiveSmallIntegerField(verbose_name='育成', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    text = models.TextField(max_length=700, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_ip_address = models.GenericIPAddressField(null=True)
    like = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'コメント（ナショナル詳細）'

    def __str__(self):
        return self.author


class NationalCommentLikeIpAddress(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    national_comment = models.ForeignKey(NationalComment, on_delete=models.CASCADE)
    comment_text = models.TextField(max_length=700, null=True, blank=True)
    ip = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    like_flg = models.CharField(max_length=50, default='1', choices=LIKE_STATE_CHOICES)
    like_click_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name_plural = 'いいね・IPアドレス（ナショナル詳細）'


class Player(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    height = models.IntegerField()
    foot = models.CharField(max_length=100, choices=DOMINANT_FOOT_CHOICES)
    main_position = models.CharField(max_length=100, choices=POSITION_CHOICES)
    second_position = models.CharField(max_length=100, null=True, blank=True, choices=POSITION_CHOICES)
    third_position = models.CharField(max_length=100, null=True, blank=True, choices=POSITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '選手'

    def save(self, *args, **kwargs):
        if self.is_public and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def avg_ratings(self):
        rating_average = self.comments.aggregate(
            Avg('ovr'),
            Avg('shoot'),
            Avg('dribble'),
            Avg('pas'),
            Avg('defense'),
            Avg('physical'),
            Avg('speed'),
            Avg('saving'),
            Avg('handling'),
            Avg('kick'),
            Avg('positioning'),
            Avg('reflexes'),
        )
        return rating_average

    def __str__(self):
        return self.name



class Comment(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=30, default='匿名')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    ovr = models.PositiveSmallIntegerField(verbose_name='総合評価', null=True, default=4, choices=OVR_CHOICES)
    ### フィールドプレイヤー評価項目 ###
    shoot = models.PositiveSmallIntegerField(verbose_name='シュート', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    dribble = models.PositiveSmallIntegerField(verbose_name='ドリブル', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    pas = models.PositiveSmallIntegerField(verbose_name='パス', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    defense = models.PositiveSmallIntegerField(verbose_name='守備力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    physical = models.PositiveSmallIntegerField(verbose_name='フィジカル', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    speed = models.PositiveSmallIntegerField(verbose_name='スピード', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    ### GK評価項目 ###
    saving = models.PositiveSmallIntegerField(verbose_name='セービング', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    handling = models.PositiveSmallIntegerField(verbose_name='ハンドリング', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    kick = models.PositiveSmallIntegerField(verbose_name='キック', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    positioning = models.PositiveSmallIntegerField(verbose_name='ポジショニング', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    reflexes = models.PositiveSmallIntegerField(verbose_name='反射神経', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    text = models.TextField(max_length=700, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_ip_address = models.GenericIPAddressField(null=True)
    like = models.IntegerField(default=0)
    
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'コメント（選手）'
        
    def __str__(self):
        return self.author


class LikeIpAddress(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    player_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    comment_text = models.TextField(max_length=700, null=True, blank=True)
    ip = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    like_flg = models.CharField(max_length=50, default='1', choices=LIKE_STATE_CHOICES)
    like_click_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name_plural = 'いいね・IPアドレス（選手）'


class Manager(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '監督'

    def avg_ratings(self):
        rating_average = self.manager_comments.aggregate(
            Avg('ovr'),
            Avg('attack'),
            Avg('defense'),
            Avg('achievement'),
            Avg('management'),
            Avg('political'),
            Avg('development'),
        )
        return rating_average

    def __str__(self):
        return self.name


class ManagerComment(models.Model):
    manager = models.ForeignKey(
        Manager, on_delete=models.CASCADE, related_name='manager_comments')
    author = models.CharField(max_length=30, default='匿名')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    ovr = models.PositiveSmallIntegerField(verbose_name='総合評価', null=True, default=4, choices=OVR_CHOICES)
    attack = models.PositiveSmallIntegerField(verbose_name='攻撃戦術', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    defense = models.PositiveSmallIntegerField(verbose_name='守備戦術', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    achievement = models.PositiveSmallIntegerField(verbose_name='実績', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    management = models.PositiveSmallIntegerField(verbose_name='マネジメント', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    development = models.PositiveSmallIntegerField(verbose_name='育成', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    political = models.PositiveSmallIntegerField(verbose_name='政治力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    text = models.TextField(max_length=700, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_ip_address = models.GenericIPAddressField(null=True)
    like = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'コメント（監督）'
        
    def __str__(self):
        return self.author


class ManagerLikeIpAddress(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, null=True)
    manager_comment = models.ForeignKey(ManagerComment, on_delete=models.CASCADE)
    comment_text = models.TextField(max_length=700, null=True, blank=True)
    ip = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    like_flg = models.CharField(max_length=50, default='1', choices=LIKE_STATE_CHOICES)
    like_click_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name_plural = 'いいね・IPアドレス（監督）'


class ManagerUpdateRequest(models.Model):
    manager_id = models.IntegerField(default=0)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '【更新リクエスト】監督'
    

class PlayerUpdateRequest(models.Model):
    player_id = models.IntegerField(default=0)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    height = models.IntegerField()
    foot = models.CharField(max_length=50, choices=DOMINANT_FOOT_CHOICES)
    main_position = models.CharField(max_length=100, choices=POSITION_CHOICES)
    second_position = models.CharField(max_length=100, null=True, blank=True, choices=POSITION_CHOICES)
    third_position = models.CharField(max_length=100, null=True, blank=True, choices=POSITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '【更新リクエスト】選手'


class ClubUpdateRequest(models.Model):
    team_id = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    year_established = models.IntegerField()
    home_town = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = '【更新リクエスト】チーム'
    

class NationalUpdateRequest(models.Model):
    country_id = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    capital = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    association = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = '【更新リクエスト】国籍'


class ManagerNewCreateRequest(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    # 以下評価コメント用
    author = models.CharField(max_length=50, default='匿名')
    ovr = models.PositiveSmallIntegerField(verbose_name='総合評価', null=True, default=4, choices=SCORE_CHOICES)
    attack_rating = models.PositiveSmallIntegerField(verbose_name='攻撃戦術', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    defense_rating = models.PositiveSmallIntegerField(verbose_name='守備戦術', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    achievement_rating = models.PositiveSmallIntegerField(verbose_name='実績', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    management_rating = models.PositiveSmallIntegerField(verbose_name='マネジメント', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    development_rating = models.PositiveSmallIntegerField(verbose_name='育成', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    political_rating = models.PositiveSmallIntegerField(verbose_name='政治力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    comment_text = models.TextField(max_length=700, null=True, blank=True)
    user_ip_address = models.GenericIPAddressField(null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '【新規追加リクエスト】監督'
    

class PlayerNewCreateRequest(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    height = models.IntegerField()
    foot = models.CharField(max_length=50, choices=DOMINANT_FOOT_CHOICES)
    main_position = models.CharField(max_length=100, choices=POSITION_CHOICES)
    second_position = models.CharField(max_length=100, null=True, blank=True, choices=POSITION_CHOICES)
    third_position = models.CharField(max_length=100, null=True, blank=True, choices=POSITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    # 以下評価コメント用
    author = models.CharField(max_length=50, default='匿名')
    ovr = models.PositiveSmallIntegerField(verbose_name='総合評価', null=True, default=4, choices=SCORE_CHOICES)
    shoot_rating = models.PositiveSmallIntegerField(verbose_name='シュート', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    dribble_rating = models.PositiveSmallIntegerField(verbose_name='ドリブル', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    pass_rating = models.PositiveSmallIntegerField(verbose_name='パス', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    defense_rating = models.PositiveSmallIntegerField(verbose_name='守備力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    physical_rating = models.PositiveSmallIntegerField(verbose_name='フィジカル', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    speed_rating = models.PositiveSmallIntegerField(verbose_name='スピード', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    comment_text = models.TextField(max_length=700, null=True, blank=True)
    user_ip_address = models.GenericIPAddressField(null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '【新規追加リクエスト】選手'


class ClubNewCreateRequest(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True)
    year_established = models.IntegerField()
    home_town = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='team_logo/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # 以下評価コメント用
    author = models.CharField(max_length=50, default='匿名')    
    ovr = models.PositiveSmallIntegerField(verbose_name='総合評価', null=True, default=4, choices=SCORE_CHOICES)
    attack_rating = models.PositiveSmallIntegerField(verbose_name='攻撃力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    defense_rating = models.PositiveSmallIntegerField(verbose_name='守備力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    manager_rating = models.PositiveSmallIntegerField(verbose_name='監督・コーチ', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    front_rating = models.PositiveSmallIntegerField(verbose_name='フロント', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    development_rating = models.PositiveSmallIntegerField(verbose_name='育成', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    comment_text = models.TextField(max_length=700, null=True, blank=True)
    user_ip_address = models.GenericIPAddressField(null=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = '【新規追加リクエスト】チーム'
    

class NationalNewCreateRequest(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True)
    flag = models.TextField(blank=True, null=True)
    capital = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    association = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    # 以下評価コメント用
    author = models.CharField(max_length=50, default='匿名')
    ovr = models.PositiveSmallIntegerField(verbose_name='総合評価', null=True, default=4, choices=SCORE_CHOICES)
    attack_rating = models.PositiveSmallIntegerField(verbose_name='攻撃力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    defense_rating = models.PositiveSmallIntegerField(verbose_name='守備力', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    manager_rating = models.PositiveSmallIntegerField(verbose_name='監督・コーチ', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    association_rating = models.PositiveSmallIntegerField(verbose_name='協会・連盟', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    development_rating = models.PositiveSmallIntegerField(verbose_name='育成', null=True, blank=True, default=4, choices=SCORE_CHOICES)
    comment_text = models.TextField(max_length=700, null=True, blank=True)
    user_ip_address = models.GenericIPAddressField(null=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = '【新規追加リクエスト】国籍'
    

class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    subject = models.CharField(max_length=150, null=True, blank=True)
    inquiry_details = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'お問い合わせ'