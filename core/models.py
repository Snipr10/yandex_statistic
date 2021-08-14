from django.db import models


class YandexStatistic(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
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

    class Meta:
        db_table = 'prsr_parser_yandex_static'
