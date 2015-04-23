$(document).ready(function() {
	/* navigation */
	$('#navigation_autocomplete').yourlabsAutocomplete({
		url: '/navigation/',
		choiceSelector: 'a',
		placeholder: "Start typing..."
	}).input.bind('selectChoice', function(e, choice, autocomplete) {
		document.location.href = choice.attr('href');
	});
	/* messages */
	var messageSelector = '#messages div';
	var messageContainer = '#messages';
	var closeSelector = '.message-close';
	var closeAllSelector = '.message-close-all';
	$.fn.messageClose = function() {
		$(this).fadeTo('fast', 0, function() {
			$(this).hide('fast', function() {
				$(this).remove();
			});
		});
	};
	$.fn.messageCloseTimeout = function(interval) {
		var _this = $(this);
		setTimeout(function() {
			_this.messageClose();
			var close = _this.find(closeSelector);
			if (close.attr('data-href') != '#') {
				$.ajax({
					url: $(this).attr('data-href')
				})
			}
		}, interval)
	};
	$(closeSelector).click(function(event) {
		event.preventDefault();
		if ($(this).attr('data-href') != '#') {
			$.ajax({
				url: $(this).attr('data-href')
			})
		}
		if ($(messageSelector).length <= 2) {
			$(closeAllSelector).messageClose();
		} else if ($(messageSelector).length <= 1) {
			$(messageContainer).messageClose();
		}
		$(this).closest(messageSelector).messageClose();
	});
	$(closeAllSelector).click(function(event) {
		event.preventDefault();
		$.ajax({
			url: $(this).attr('href')
		})
		$(this).messageClose();
		$(messageSelector).messageClose();
		$(messageContainer).messageClose();
	});
});