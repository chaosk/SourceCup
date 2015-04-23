from django import template
from django.core import urlresolvers
from ..models import Round


register = template.Library()

PLAYOFF_ROUNDS = (
	u"Final",
	u"Semi-finals",
	u"Quarter-finals",
	u"1/8th Finals",
)

@register.simple_tag
def round_name(round, tournament):
	if round.round_type == Round.ROUND_TYPE_LADDER:
		return u"Round {0}".format(round.number)
	elif round.round_type == Round.ROUND_TYPE_PLAYOFF:
		try:
			name = PLAYOFF_ROUNDS[(tournament.season.ladder_rounds+tournament.season.playoff_rounds)-round.number]
		except IndexError:
			name = u"Play-off Round {0}".format(round.number-tournament.season.ladder_rounds)
		return name
