from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from .tasks import update_profiles
from .utils import STEAMID_MAGIC, get_state_display
from .utils import API_PERSONA_STATE_OFFLINE, API_PERSONA_STATE_BUSY


STEAMCOMMUNITY_URL = "http://steamcommunity.com"


class SteamUserManager(BaseUserManager):

	def create_user(self, steamid):
		"""Creates and saves a SteamUser with the given steamid"""
		if not steamid:
			raise ValueError("User must have a steamid64")

		user = self.model(
			steamid=steamid
		)
		user.save(using=self._db)
		return user

	def create_superuser(self, steamid):
		"""
		Creates and saves a SteamUser with
		admin privileges and given steamid
		"""
		if not steamid:
			raise ValueError("User must have a steamid64")

		user = self.model(
			steamid=steamid,
			level=SteamUser.LEVEL_SUPERHERO
		)
		user.save(using=self._db)
		return user


class SteamUser(AbstractBaseUser):
	"""Model for Steam OpenID authentication."""

	"""steamid holds steamid64 received from a successful login"""
	steamid = models.BigIntegerField(unique=True, db_index=True,
		verbose_name="SteamID64")

	email = models.CharField(max_length=255, blank=True,
		verbose_name="E-mail address")
	wants_emails = models.BooleanField(default=True)

	freeze_username = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)

	username = models.CharField(max_length=100, blank=True)
	profile_url = models.CharField(max_length=255, blank=True)
	avatar = models.CharField(max_length=255, blank=True)
	avatar_full = models.CharField(max_length=255, blank=True)
	description = models.CharField(max_length=255, blank=True)

	is_active = models.BooleanField(default=True)
	
	LEVEL_SUPERHERO = 9
	LEVEL_JUSTAHERO = 6
	LEVEL_SIDEKICK = 3
	LEVEL_USER = 1
	LEVEL_CHOICES = (
		(LEVEL_SUPERHERO, "Owner"),
		(LEVEL_JUSTAHERO, "Admin"),
		(LEVEL_SIDEKICK, "Helper"),
		(LEVEL_USER, "User"),
	)
	level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES,
		default=LEVEL_USER)

	objects = SteamUserManager()

	USERNAME_FIELD = 'steamid'
	REQUIRED_FIELDS = []

	class Meta:
		ordering = ['created_at']

	def get_absolute_url(self):
		return reverse('user_details', args=[str(self.steamid)])

	def get_team(self):
		return self.teams.latest('id')

	def __str__(self):
		return self.username or str(self.steamid)

	get_short_name = __str__
	get_full_name = __str__

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def vanity_url(self):
		return self.profile_url[len(STEAMCOMMUNITY_URL):]

	@property
	def is_caster(self):
		return self.level >= SteamUser.LEVEL_CASTER

	@property
	def is_staff(self):
		return self.level >= SteamUser.LEVEL_SIDEKICK

	@property
	def is_hero(self):
		return self.level >= SteamUser.LEVEL_JUSTAHERO

	@property
	def persona_state(self):
		return cache.get('user_{0}_state'.format(self.steamid))

	@property
	def persona_state_display(self):
		return get_state_display(self.persona_state)

	@property
	def persona_game(self):
		return cache.get('user_{0}_game'.format(self.steamid))

	@property
	def persona_yesno(self):
		"""
		yesno template Helper

		Returns True if self is playing a game.
		Returns False if self is online.
		Returns None if self is offline or busy.
		"""
		if self.persona_state in (API_PERSONA_STATE_OFFLINE, API_PERSONA_STATE_BUSY):
			return None
		return self.persona_game

	def to_communityid32(self):
		return "[U:1:{}]".format(self.steamid-STEAMID_MAGIC)

	def to_steamid32(self):
		return "STEAM_0:{0}:{1}".format(
			self.steamid % 2, (self.steamid-STEAMID_MAGIC)/2)


class Nonce(models.Model):
	server_url = models.CharField(max_length=2047)
	timestamp = models.IntegerField()
	salt = models.CharField(max_length=40)

	def __unicode__(self):
		return u"Nonce: %s, %s" % (self.server_url, self.salt)


class Association(models.Model):
	server_url = models.TextField(max_length=2047)
	handle = models.CharField(max_length=255)
	secret = models.TextField(max_length=255) # Stored base64 encoded
	issued = models.IntegerField()
	lifetime = models.IntegerField()
	assoc_type = models.TextField(max_length=64)

	def __unicode__(self):
		return u"Association: %s, %s" % (self.server_url, self.handle)


@receiver(user_logged_in)
def update_profile_signal(sender, **kwargs):
	#update_profiles.delay((kwargs['user'].id,))
	update_profiles((kwargs['user'].id,))
