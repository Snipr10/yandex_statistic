# Generated by Django 3.1.4 on 2021-08-14 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='YandexStatistic',
            fields=[
                ('id', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('url', models.CharField(max_length=256)),
                ('lastHourDocs', models.IntegerField()),
                ('storyDocs', models.IntegerField()),
                ('themeStories', models.IntegerField()),
                ('themeDocs', models.IntegerField()),
                ('fullWatches', models.FloatField()),
                ('regionalInterest', models.IntegerField()),
                ('generalInterest', models.IntegerField()),
                ('weight', models.IntegerField()),
                ('parsing_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'prsr_parser_tg_proxy',
            },
        ),
    ]