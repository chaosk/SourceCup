# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tournament.models
import uuid
import django.core.validators
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(help_text='Config name', max_length=70)),
                ('slug', models.CharField(help_text='Config short name (also its filename)', max_length=70, unique=True)),
                ('extension', models.CharField(max_length=5, default='cfg')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('config_file', models.FileField(upload_to=tournament.models.config_file_name)),
            ],
        ),
        migrations.CreateModel(
            name='GameServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('address', models.GenericIPAddressField()),
                ('port', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(65535)])),
                ('api_key', models.UUIDField(default=uuid.uuid4)),
                ('last_heartbeat', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('slug', models.CharField(help_text='Map name (also its filename)', max_length=70, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('map_file', models.FileField(upload_to=tournament.models.map_file_name)),
                ('config', models.ForeignKey(blank=True, to='tournament.Config', null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('status', models.CharField(max_length=1, choices=[('S', 'Scheduled'), ('R', 'Reported'), ('A', 'Accepted'), ('C', 'Contested'), ('E', 'Resolved'), ('D', 'Double forfeit'), ('B', 'Bye')], default='S')),
                ('gameserver', models.ForeignKey(blank=True, null=True, to='tournament.GameServer')),
            ],
        ),
        migrations.CreateModel(
            name='MatchResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('score', models.PositiveSmallIntegerField(null=True)),
                ('opponents_score', models.PositiveSmallIntegerField(null=True)),
                ('is_defaultloss', models.BooleanField(default=False)),
                ('is_defaultwin', models.BooleanField(default=False)),
                ('match', models.ForeignKey(related_name='results', to='tournament.Match')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('joined_at', models.DateTimeField(blank=True, null=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('player', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=70)),
                ('short_name', models.CharField(blank=True, max_length=50)),
                ('slug', models.CharField(max_length=70, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('number', models.PositiveSmallIntegerField(null=True)),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField()),
                ('is_scheduled', models.BooleanField(default=False)),
                ('is_postprocessed', models.BooleanField(default=False)),
                ('round_type', models.CharField(max_length=1, choices=[('L', 'Ladder'), ('P', 'Play-off')])),
                ('map', models.ForeignKey(blank=True, to='tournament.Map', null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=70)),
                ('short_name', models.CharField(blank=True, max_length=50)),
                ('slug', models.CharField(max_length=70, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=70)),
                ('tag', models.CharField(max_length=25)),
                ('leader', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, related_name='owned_teams', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('members', models.ManyToManyField(blank=True, related_name='teams', through='tournament.Membership', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TeamEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('is_ready', models.BooleanField(default=False)),
                ('is_suspended', models.BooleanField(default=False)),
                ('suspended_at', models.DateTimeField(blank=True, null=True)),
                ('suspended_for', models.CharField(blank=True, max_length=255)),
                ('rank', models.SmallIntegerField(default=99)),
                ('tiebreaker', models.SmallIntegerField(default=0)),
                ('is_alive', models.NullBooleanField(default=None)),
                ('opponents', models.ManyToManyField(related_name='opponents_rel_+', to='tournament.TeamEntry')),
                ('suspended_by', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(related_name='entries', to='tournament.Team')),
            ],
        ),
        migrations.CreateModel(
            name='TeamEntrySnapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('round_number', models.PositiveSmallIntegerField()),
                ('rank', models.SmallIntegerField(default=99)),
                ('is_alive', models.NullBooleanField(default=None)),
                ('forfeits', models.PositiveSmallIntegerField(default=0)),
                ('matches_played', models.PositiveSmallIntegerField(default=0)),
                ('ladder_points', models.PositiveSmallIntegerField(default=0)),
                ('ladder_points_won', models.PositiveSmallIntegerField(default=0)),
                ('ladder_points_lost', models.PositiveSmallIntegerField(default=0)),
                ('match_points', models.PositiveSmallIntegerField(default=0)),
                ('match_points_won', models.PositiveSmallIntegerField(default=0)),
                ('match_points_lost', models.PositiveSmallIntegerField(default=0)),
                ('team_entry', models.ForeignKey(related_name='snapshots', to='tournament.TeamEntry')),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=70)),
                ('short_name', models.CharField(blank=True, max_length=50)),
                ('slug', models.CharField(max_length=70, unique=True)),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField(blank=True, null=True)),
                ('state', models.CharField(max_length=1, choices=[('O', 'Open'), ('C', 'Closed'), ('P', 'Pending'), ('I', 'In progress'), ('F', 'Finished')], default='O')),
                ('ladder_rounds', models.PositiveSmallIntegerField()),
                ('playoff_rounds', models.PositiveSmallIntegerField()),
                ('region', models.ForeignKey(to='tournament.Region')),
                ('season', models.ForeignKey(to='tournament.Season')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=70)),
                ('short_name', models.CharField(max_length=70)),
            ],
        ),
        migrations.AddField(
            model_name='teamentry',
            name='tournament',
            field=models.ForeignKey(related_name='team_entries', to='tournament.Tournament'),
        ),
        migrations.AddField(
            model_name='season',
            name='tournament_base',
            field=models.ForeignKey(to='tournament.TournamentBase'),
        ),
        migrations.AddField(
            model_name='round',
            name='tournament',
            field=models.ForeignKey(related_name='rounds', to='tournament.Tournament'),
        ),
        migrations.AddField(
            model_name='membership',
            name='team',
            field=models.ForeignKey(to='tournament.Team'),
        ),
        migrations.AddField(
            model_name='matchresult',
            name='opponent',
            field=models.ForeignKey(blank=True, null=True, to='tournament.TeamEntry'),
        ),
        migrations.AddField(
            model_name='matchresult',
            name='team_entry',
            field=models.ForeignKey(related_name='results', to='tournament.TeamEntry'),
        ),
        migrations.AddField(
            model_name='match',
            name='home_team_entry',
            field=models.ForeignKey(blank=True, to='tournament.TeamEntry', related_name='home_matches', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='match',
            name='round',
            field=models.ForeignKey(related_name='matches', to='tournament.Round'),
        ),
        migrations.AddField(
            model_name='match',
            name='team_entries',
            field=models.ManyToManyField(related_name='matches', through='tournament.MatchResult', to='tournament.TeamEntry'),
        ),
        migrations.AddField(
            model_name='match',
            name='winner_team_entry',
            field=models.ForeignKey(blank=True, related_name='won_matches', null=True, to='tournament.TeamEntry'),
        ),
    ]
