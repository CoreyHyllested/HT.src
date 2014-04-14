//view more/less functionality used on the profile page
//number of characters allowed in the text before clicking the button
var max_text_length = 490
	$(function(){
		var text = $('#about_text').html();
		if (text) {
		  var extract = text.substring(0,max_text_length) + "...";
		};
		//create the button if there is more text than maximum allowed
		if (text.length > max_text_length) {
		  $('#about_text').html(extract);
		  $('#button').html('<a href="#" class="more">View More</a>');
		  more(text);
	  };
	});	

	this.more = function(text){	
	$('.more').click(function () {
			$('#about_text').html(text);
			$('#about_text').append('<div class="position"></div>');
			//adjust the positioning and display more text
			position();
			//display view less button
			$('#button').html('<a href="#" class="less">View Less</a>');
			return false;
		});
	}

	this.position = function(){	
		var p = $(".position");
		var position = p.position();
		var pos_top = position.top - 72;
		//animate the expansion and appearance of new text
		$('#about_text').animate({height:pos_top+'px'}, function(){
			less();
		});	
	}

	this.less = function(){	
	$('.less').click(function () {
		$('#about_text').animate({height:'134px'}, function(){
			var text = $('#about_text').html();
			var extract = text.substring(0,max_text_length) + "...";
			$('#about_text').html(extract);
			//display less text and view more button
			$('#button').html('<a href="#" class="more">View More</a>');
			more(text);
			});	
			return false;
		});
	}