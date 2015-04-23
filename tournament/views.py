from django.shortcuts import render, get_object_or_404
from .models import Tournament, Round

def tournament_list(request):
	return render(request, 'tournament/tournament_list.html', {
		'tournaments': Tournament.objects.all(),
	})


def tournament_details_results(request, slug, round_number):
	around = get_object_or_404(Round,
		tournament__slug=slug, number=round_number)
	return render(request, 'tournament/tournament_details_results.html', {
		'tournament': around.tournament,
		'rounds': around.tournament.rounds.order_by('number'),
		'round': around,
		'results': list(MatchResult.objects.filter(match__round=around).select_related('match', 'opponent').filter(team_entry=F('match__home_team_entry')).order_by('-match__status')),
	})


def tournament_details_fixtures(request, slug):
	tournament = get_object_or_404(Tournament, slug=slug)
	around = tournament.current_round
	context = {
		'tournament': tournament,
		'round': around,
	}
	if around:
		context['matches'] = around.matches.filter(status=Match.STATUS_SCHEDULED)
	return render(request, 'tournament/tournament_details_fixtures.html', context)


def tournament_details(request, slug, page='teams'):
	tournament = get_object_or_404(Tournament, slug=slug)
	template_name = 'tournament/tournament_details.html'
	if page in ('teams', 'schedule', 'results'):
		template_name = 'tournament/tournament_details_{0}.html'.format(page)
	context = {
		'tournament': tournament,
		'rounds': tournament.rounds.order_by('number'),
	}
	if page == 'teams':
		context['team_entries'] = tournament.team_entries.select_related('team').filter(is_suspended=False).order_by(
			'rank',
			#'-ladder_points', '-ladder_points_won', '-match_points',
			#'forfeits', '-match_points_won', 'matches_played', '-tiebreaker')
		)
	elif page == 'schedule':
		context['rounds'] = tournament.rounds.select_related('map').order_by('number')
	return render(request, template_name, context)