import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class SnapshotException(Exception):
	pass


class TournamentBase(models.Model):
	name = models.CharField(max_length=70)
	short_name = models.CharField(max_length=70)

	def __str__(self):
		return self.name


class Season(models.Model):
	tournament_base = models.ForeignKey(TournamentBase)
	name = models.CharField(max_length=70)
	short_name = models.CharField(max_length=50, blank=True)
	slug = models.CharField(max_length=70, unique=True)

	starts_at = models.DateTimeField(default=datetime.now)
	ends_at = models.DateTimeField(null=True, blank=True)

	"""
	Teams are free to sign up
	"""
	STATE_OPEN = 'O'

	"""
	Teams cannot sign up, but staff can modify tournament properties
	(including adding new teams)
	"""
	STATE_CLOSED = 'C'

	"""
	All properties are frozen, tournament has been generated.
	"""
	STATE_PENDING = 'P'

	"""
	First round has started.
	"""
	STATE_IN_PROGRESS = 'I'

	"""
	Last round has ended.
	"""
	STATE_FINISHED = 'F'

	STATE_CHOICES = (
		(STATE_OPEN, "Open"),
		(STATE_CLOSED, "Closed"),
		(STATE_PENDING, "Pending"),
		(STATE_IN_PROGRESS, "In progress"),
		(STATE_FINISHED, "Finished")
	)
	state = models.CharField(max_length=1, choices=STATE_CHOICES,
		default=STATE_OPEN)

	"""
	ladder_rounds specifies how many ladder rounds will be played.

	Setting this to zero enforces playoff_rounds = ceil(log2(number_of_teams))
	(meaning tournament becomes single elimination).

	This field cannot be changed after tournament has been created.
	"""
	ladder_rounds = models.PositiveSmallIntegerField(default=0)

	"""
	playoff_rounds set to:
	  - 0 will disable play-offs.
	  - 1 will cause best two teams play in a final.
	  - 2 will cause best four teams play in semifinals and in a final.
	  and so on

	This field cannot be changed after tournament has been created.
	"""
	playoff_rounds = models.PositiveSmallIntegerField(default=0)

	def __str__(self):
		return "{} {}".format(self.tournament_base, self.name)

	def save(self, *args, **kwargs):
		created = not self.id
		if created:
			self.ends_at = self.starts_at \
				+ timedelta(days=7*(self.ladder_rounds+self.playoff_rounds))
		super().save(*args, **kwargs)


class Region(models.Model):
	name = models.CharField(max_length=70)
	short_name = models.CharField(max_length=50, blank=True)
	slug = models.CharField(max_length=70, unique=True)

	def __str__(self):
		return self.name


class Tournament(models.Model):
	season = models.ForeignKey(Season)
	region = models.ForeignKey(Region)

	name = models.CharField(max_length=70)
	short_name = models.CharField(max_length=50, blank=True)
	slug = models.CharField(max_length=70, unique=True)

	class Meta:
		unique_together = ('season', 'region')

	@property
	def current_round(self):
		try:
			around = self.rounds.filter(ends_at__gt=timezone.now()).order_by('number')[0]
		except IndexError:
			around = None
		return around

	def get_absolute_url(self):
		return reverse('tournament_details', args=[self.slug])

	def __str__(self):
		return "{} {}".format(self.season, self.region)

	def save(self, *args, **kwargs):
		created = not self.id
		super().save(*args, **kwargs)
		if created:
			season = self.season
			for number in range(season.ladder_rounds+season.playoff_rounds):
				Round.objects.create(number=number+1, tournament=self,
					starts_at=season.starts_at+timedelta(days=7*(number)),
					ends_at=season.starts_at+timedelta(days=7*(number)+6),
					round_type=Round.ROUND_TYPE_LADDER \
						if number < season.ladder_rounds else Round.ROUND_TYPE_PLAYOFF
				)


def map_file_name(instance, filename):
	"""
	Determines map path and file name.
	"""
	return 'maps/{0}.bsp'.format(instance.slug)


class Map(models.Model):
	slug = models.CharField(unique=True, max_length=70,
			help_text="Map name (also its filename)")
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now=True)
	map_file = models.FileField(upload_to=map_file_name)
	
	config = models.ForeignKey('Config', null=True, blank=True,
		on_delete=models.SET_NULL)

	def get_absolute_url(self):
		return reverse('map_details', args=[self.slug])

	def __str__(self):
		return self.slug


def config_file_name(instance, filename):
	"""
	Determines config path and file name.
	"""
	return 'configs/{0}.{1}'.format(instance.slug,
		instance.extension)


class Config(models.Model):
	name = models.CharField(max_length=70, help_text="Config name")
	slug = models.CharField(unique=True, max_length=70,
		help_text="Config short name (also its filename)")
	extension = models.CharField(max_length=5,
		default='cfg')
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now=True)
	description = models.CharField(max_length=255, blank=True)
	config_file = models.FileField(upload_to=config_file_name)

	def get_absolute_url(self):
		return reverse('config_details', args=[self.slug])

	def __str__(self):
		return self.name


class Round(models.Model):
	"""
	Number of rounds is based on number
	of entrants and number of groups.

	Total number of rounds is
	  group stage rounds + play-off rounds
	"""
	number = models.PositiveSmallIntegerField(null=True)
	tournament = models.ForeignKey(Tournament, related_name='rounds')

	map = models.ForeignKey('Map', null=True, blank=True,
		on_delete=models.SET_NULL)

	starts_at = models.DateTimeField()
	ends_at = models.DateTimeField()

	"""
	Defines whether match pairs have been generated.
	"""
	is_scheduled = models.BooleanField(default=False)

	is_postprocessed = models.BooleanField(default=False)

	ROUND_TYPE_LADDER = 'L'
	ROUND_TYPE_PLAYOFF = 'P'
	ROUND_TYPE_CHOICES = (
		(ROUND_TYPE_LADDER, 'Ladder'),
		(ROUND_TYPE_PLAYOFF, 'Play-off'),
	)
	round_type = models.CharField(max_length=1, choices=ROUND_TYPE_CHOICES)

	def has_started(self):
		return self.starts_at <= timezone.now()

	def has_ended(self):
		return self.ends_at <= timezone.now()

	def is_happening(self):
		# return self.has_started() and not self.has_ended()
		return self.starts_at <= timezone.now() < self.ends_at

	def __str__(self):
		return "Round {0}".format(self.number)

	def generate_pairs(self):
		...

	def save(self, *args, **kwargs):
		created = not self.id
		if created:
			try:
				last_round = Round.objects.filter(
					tournament=self.tournament).order_by('-number')[0]
				number = last_round.number + 1
			except IndexError:
				number = 1
			self.number = number
		super(Round, self).save(*args, **kwargs)


class Match(models.Model):
	round = models.ForeignKey(Round, related_name='matches')

	home_team_entry = models.ForeignKey('TeamEntry', related_name='home_matches',
		on_delete=models.SET_NULL, null=True, blank=True)
	team_entries = models.ManyToManyField('TeamEntry', through='MatchResult',
		through_fields=('match', 'team_entry'), related_name='matches')
	winner_team_entry = models.ForeignKey('TeamEntry', related_name='won_matches',
		null=True, blank=True)
	gameserver = models.ForeignKey('GameServer', null=True, blank=True)

	STATUS_SCHEDULED = 'S'
	STATUS_REPORTED = 'R'
	STATUS_ACCEPTED = 'A'
	STATUS_CONTESTED = 'C'
	STATUS_RESOLVED = 'E'
	STATUS_DEFAULTLOSS = 'D'
	STATUS_BYE = 'B'
	STATUS_CHOICES = (
		(STATUS_SCHEDULED, "Scheduled"),
		(STATUS_REPORTED, "Reported"),
		(STATUS_ACCEPTED, "Accepted"),
		(STATUS_CONTESTED, "Contested"),
		(STATUS_RESOLVED, "Resolved"),
		(STATUS_DEFAULTLOSS, "Double forfeit"),
		(STATUS_BYE, "Bye"),
	)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES,
		default=STATUS_SCHEDULED)


class MatchResult(models.Model):
	"""
	Intermediary model for M2M relation between Match and TeamEntry.
	"""
	match = models.ForeignKey(Match, related_name='results')
	team_entry = models.ForeignKey('TeamEntry', related_name='results')
	opponent = models.ForeignKey('TeamEntry', null=True, blank=True)
	score = models.PositiveSmallIntegerField(null=True)
	opponents_score = models.PositiveSmallIntegerField(null=True)

	is_defaultloss = models.BooleanField(default=False)
	is_defaultwin = models.BooleanField(default=False)


class Team(models.Model):
	name = models.CharField(max_length=70)
	tag = models.CharField(max_length=25)
	leader = models.ForeignKey(settings.AUTH_USER_MODEL,
		null=True, blank=True,
		related_name='owned_teams', on_delete=models.SET_NULL)

	members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams',
		through='Membership', blank=True)

	def __str__(self):
		return self.name


class TeamEntry(models.Model):
	"""
	Intermediary model for M2M relation between Tournament and Team.
	"""

	tournament = models.ForeignKey(Tournament, related_name='team_entries')
	team = models.ForeignKey(Team, related_name='entries')

	opponents = models.ManyToManyField("self")

	is_ready = models.BooleanField(default=False)

	# @TODO refactor to Infraction model
	# 
	is_suspended = models.BooleanField(default=False)
	suspended_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
	suspended_at = models.DateTimeField(blank=True, null=True)
	suspended_for = models.CharField(max_length=255, blank=True)

	# @TODO how do i denorm this
	rank = models.SmallIntegerField(default=99)

	# @TODO find out what tiebreaker points were given for
	tiebreaker = models.SmallIntegerField(default=0)

	# these are used in ladder
	def forfeits(self):
		return self.results.filter(is_defaultloss=True).count()

	def matches_played(self):
		return self.results.filter(
			match__status__in=(Match.STATUS_ACCEPTED, Match.STATUS_RESOLVED,
				Match.STATUS_BYE, Match.STATUS_DEFAULTLOSS)).filter(is_defaultloss=False).count()

	@property
	def ladder_points(self):
		return self.ladder_points_won - self.ladder_points_lost

	def ladder_points_won(self):
		return self.results.filter(
			match__status__in=(Match.STATUS_ACCEPTED, Match.STATUS_RESOLVED,
				Match.STATUS_BYE, Match.STATUS_DEFAULTLOSS)).filter(is_victory=True).count()

	def ladder_points_lost(self):
		return self.results.filter(
			match__status__in=(Match.STATUS_ACCEPTED, Match.STATUS_RESOLVED,
				Match.STATUS_BYE, Match.STATUS_DEFAULTLOSS)).filter(is_victory=False).count()

	@property
	def match_points(self):
		return self.match_points_won - self.match_points_lost

	def match_points_won(self):
		return self.results.filter(
			match__status__in=(Match.STATUS_ACCEPTED, Match.STATUS_RESOLVED,
				Match.STATUS_BYE, Match.STATUS_DEFAULTLOSS)).aggregate(
			score_sum=Sum('score'))['score_sum'] or 0

	def match_points_lost(self):
		return self.results.filter(
			match__status__in=(Match.STATUS_ACCEPTED, Match.STATUS_RESOLVED,
				Match.STATUS_BYE, Match.STATUS_DEFAULTLOSS)).aggregate(
			opponents_score_sum=Sum('opponents_score'))['opponents_score_sum'] or 0

	# these are used in playoffs
	is_alive = models.NullBooleanField(default=None)

	def take_snapshot(self, round_number=None):
		# @FIXME decide whether to use current or previous round
		if not round_number:
			current_round = self.tournament.current_round
			if not current_round:
				raise SnapshotException("round_number argument not provided and there's currently no round being played")
			round_number = current_round.round_number
		if self.snapshots.objects.filter(round_number=round_number).exists():
			raise SnapshotException("A snaphot for this round has already been taken.")
		self.round_number = round_number
		self.team_entry = self
		keys = ['round_number', 'team_entry', 'rank', 'is_alive', 'forfeits', 'matches_played',
			'ladder_points', 'ladder_points_won', 'ladder_points_lost',
			'match_points', 'match_points_won', 'match_points_lost']
		snapshot = TeamEntrySnapshot.objects.create(**dict((key, getattr(self, key)) for key in keys))
		del self.round_number
		del self.team_entry
		return snapshot

	class Meta:
		verbose_name_plural = "Team Entries"

	def __str__(self):
		return "{0} in {1}".format(self.team, self.tournament)


class TeamEntrySnapshot(models.Model):
	"""
	It's supposed to be a TeamEntry representation after each round.
	"""
	team_entry = models.ForeignKey('TeamEntry', related_name="snapshots")
	round_number = models.PositiveSmallIntegerField()

	rank = models.SmallIntegerField(default=99)
	is_alive = models.NullBooleanField(default=None)
	forfeits = models.PositiveSmallIntegerField(default=0)
	matches_played = models.PositiveSmallIntegerField(default=0)
	ladder_points = models.PositiveSmallIntegerField(default=0)
	ladder_points_won = models.PositiveSmallIntegerField(default=0)
	ladder_points_lost = models.PositiveSmallIntegerField(default=0)
	match_points = models.PositiveSmallIntegerField(default=0)
	match_points_won = models.PositiveSmallIntegerField(default=0)
	match_points_lost = models.PositiveSmallIntegerField(default=0)


class Membership(models.Model):
	player = models.ForeignKey(settings.AUTH_USER_MODEL)
	team = models.ForeignKey(Team)
	joined_at = models.DateTimeField(null=True, blank=True)
	left_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return "{} of {}".format(self.player, self.team)


class GameServer(models.Model):
	# Source does not support IPv6, but who cares
	address = models.GenericIPAddressField()
	port = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),
		MaxValueValidator(65535)])
	api_key = models.UUIDField(default=uuid.uuid4)
	last_heartbeat = models.DateTimeField(null=True, blank=True)
	region = models.ForeignKey(Region, blank=True, null=True)

	def __str__(self):
		return "{}:{}".format(self.address, self.port)