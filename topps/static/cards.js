selected = [];
callbacks = {};

function toggleSelected(id) {
	var index;
	if ((index = selected.indexOf(id)) > -1)
		selected.splice(index, 1);
	else
		selected.push(id);
	trigger("selected");
}

function register(event, func) {
	if (!(event in callbacks)) {
		callbacks[event] = [];
	}
	callbacks[event].push(func);
}

function trigger(event) {
	if (event in callbacks)
		$.each(callbacks[event], function(index, func) {
			func();
		});
}

$(function() {

	var card = $('.card'),
		cardWidth = card.width(),
		cardHeight = card.height();


	$('.flip').on("click", function(e) {
		e.stopPropagation();
		$(this).parents('.card').toggleClass("flipped");
	});
	
	$('.card img').each(function(i, ele) {
		var $this = $(ele);

		$this.load(function() {
			console.count()
			var	width = $this.width(),
				height = $this.height(),
				newWidth = width / (height/cardHeight);

			if (newWidth < cardWidth) {
				$this.width(cardWidth);
			}
			else {
				$this.height(cardHeight);
			}
		});	
	});

	$('.card').click(function() {
		var id = $(this).attr('data-id');
		$(this).toggleClass('selected');
		toggleSelected(id);
	});

	$('.card .front').hover(function() {
		var $this = $(this);
		$(this).stop().find('.caption').slideDown(100, function() {
			$this.find('.flip').delay(50).slideDown(100);
		});
	}, function() {
		$(this).find('.caption').stop().slideUp();
		$(this).find('.flip').stop().hide();
	});

	function resizr() {
		var offset = ($(window).width()-980)/2;
		$('.cards').css({marginLeft: offset + "px"});
	};

	$(window).resize(resizr);

	resizr();


});