from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tournament, Round, Team, Membership, Season, TeamEntry


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


def tournament_join(request, slug):
	tournament = get_object_or_404(Tournament, slug=slug, season__state=Season.STATE_OPEN)
	team = request.user.current_team
	if team.leader != request.user:
		messages.error(request, "You don't have permission to join a tournament with your team.")
		return redirect(tournament.get_absolute_url())

	if team.tournaments.filter(pk=tournament.pk).exists():
		messages.error(request, "You've already joined this tournament")
		return redirect(tournament.get_absolute_url())

	entry = TeamEntry(tournament=tournament, team=team)
	entry.save()

	messages.success(request, "Your team has joined {}".format(tournament))
	return redirect(tournament.get_absolute_url())


def team_details(request, team_id):
	return render(request, 'tournament/team_details.html', {
		'team': get_object_or_404(Team, pk=team_id)
	})


@login_required
def team_leave(request, team_id):
	team = get_object_or_404(Team, pk=team_id)
	membership = get_object_or_404(Membership,
		team=team, player=request.user, left_at__isnull=True)

	if request.user == team.leader:
		messages.warning(request, "You can't leave your own team. Transfer ownership first or disband the team instead.")
		return redirect(team.get_absolute_url())

	if request.method == 'POST' and request.POST.get('confirm', False):
		messages.success(request, "You left {}".format(team))
		membership.leave()
		return redirect(team.get_absolute_url())

	return render(request, 'tournament/team_leave.html', {
		'team': team,
	})


@login_required
def team_disband(request, team_id):
	team = get_object_or_404(Team, pk=team_id, leader=request.user)
	membership = get_object_or_404(Membership,
		team=team, player=request.user, left_at__isnull=True)

	if request.method == 'POST' and request.POST.get('confirm', False):
		messages.success(request, "You disbanded {}".format(team))
		team.disband()
		return redirect(reverse('home'))

	return render(request, 'generic_confirmation.html', {
		'confirmation_message': "Are you sure you want to disband {}?"
		" There won't be a way to restore it.".format(team),
	})


@login_required
def team_edit(request, team_id):
	team = get_object_or_404(Team, pk=team_id, leader=request.user)
	membership = get_object_or_404(Membership,
		team=team, player=request.user, left_at__isnull=True)

	if request.method == 'POST' and request.POST.get('confirm', False):
		form.save()
		messages.success(request, "Your changes have been saved")
		return redirect(team.get_absolute_url())

	return render(request, 'tournament/team_edit.html', {
		'team': team,
		'form': form,
	})


@login_required
def team_create(request):
	...


@login_required
def team_join(request, team_id):
	...
