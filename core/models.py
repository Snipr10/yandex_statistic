import datetime

from django.db import models


class MyEnum(models.TextChoices):
    VALUE1 = 'Saint_Petersburg', 'Saint_Petersburg'
    VALUE2 = 'saint-petersburg_and_leningrad_oblast', 'saint-petersburg_and_leningrad_oblast'


# Добавьте поле ENUM в вашу модель
status = models.CharField(
    max_length=10,
    choices=MyEnum.choices,
    default=MyEnum.VALUE1,
)
class YandexStatistic(models.Model):
    # id = models.CharField(primary_key=True, max_length=256)
    title = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    lastHourDocs = models.IntegerField()
    storyDocs = models.IntegerField()
    themeStories = models.IntegerField()
    themeDocs = models.IntegerField()
    fullWatches = models.FloatField()
    regionalInterest = models.IntegerField()
    generalInterest = models.IntegerField()
    weight = models.IntegerField()
    parsing_date = models.DateTimeField()
    yandex_id = models.CharField(max_length=256)
    group_id = models.CharField(max_length=256)
    source = models.CharField(
        max_length=10,
        choices=MyEnum.choices,
        default=MyEnum.VALUE1,
    )

    class Meta:
        db_table = 'prsr_parser_yandex_static'


class YandexStatistic0(models.Model):
    # id = models.CharField(primary_key=True, max_length=256)
    title = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    lastHourDocs = models.IntegerField()
    storyDocs = models.IntegerField()
    themeStories = models.IntegerField()
    themeDocs = models.IntegerField()
    fullWatches = models.FloatField()
    regionalInterest = models.IntegerField()
    generalInterest = models.IntegerField()
    weight = models.IntegerField()
    parsing_date = models.DateTimeField()
    yandex_id = models.CharField(max_length=256)
    group_id = models.CharField(max_length=256)
    source = models.CharField(
        max_length=10,
        choices=MyEnum.choices,
        default=MyEnum.VALUE1,
    )
    class Meta:
        db_table = 'prsr_parser_yandex_static_0'


class Post(models.Model):
    cache_id = models.IntegerField(primary_key=True)
    owner_sphinx_id = models.IntegerField()
    created = models.DateTimeField(null=True, blank=True)
    keyword_id = models.IntegerField(default=0)
    trust = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True)
    group_id = models.CharField(max_length=255, null=True, blank=True)
    found_date = models.DateField(auto_now_add=True)
    parsing = models.IntegerField(default=0)

    class Meta:
        db_table = 'prsr_parser_global_posts'


class PostContentGlobal(models.Model):
    cache_id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=10000002, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'prsr_parser_global_post_content'


class PostGroupsGlobal(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    post_count = models.IntegerField(default=0, null=True, blank=True)
    post_count_soc = models.IntegerField(default=0, null=True, blank=True)
    found_date = models.DateField(auto_now_add=True)
    taken = models.IntegerField(default=0, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True)
    last_modified = models.CharField(max_length=255, null=True, blank=True, default="0001-01-01 00:00:00")

    class Meta:
        db_table = 'prsr_parser_global_groups'


class ApiKeysModel(models.Model):
    id = models.IntegerField(primary_key=True)
    key = models.CharField(max_length=256)
    value = models.CharField(max_length=256)

    class Meta:
        db_table = 'prsr_parser_api_keys'
