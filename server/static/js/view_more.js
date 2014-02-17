	$(function(){
		var text = $('#about_text').html();
		if (text) {
		  var extract = text.substring(0,490) + "...";
		};
		if (text.length > 490) {
		  $('#about_text').html(extract);
		  $('#button').html('<a href="#" class="more">View More</a>');
		  more(text);
	  };
	});	

	this.more = function(text){	
	$('.more').click(function () {
			$('#about_text').html(text);
			$('#about_text').append('<div class="position"></div>');
			position();
			$('#button').html('<a href="#" class="less">View Less</a>');
			return false;
		});
	}

	this.position = function(){	
		var p = $(".position");
		var position = p.position();
		var pos_top = position.top - 72;
		$('#about_text').animate({height:pos_top+'px'}, function(){
			less();
		});	
	}

	this.less = function(){	
	$('.less').click(function () {
		$('#about_text').animate({height:'134px'}, function(){
			var text = $('#about_text').html();
			var extract = text.substring(0,490) + "...";
			$('#about_text').html(extract);
			$('#button').html('<a href="#" class="more">View More</a>');
			more(text);
			});	
			return false;
		});
	}