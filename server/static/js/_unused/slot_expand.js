//expanding timeslots
$(document).ready(function() {
	$('div.slot-expand').hide();
	$('div.time-slot').click(function() {
		$ts = $(this).attr("id")
		$('#slot-expand-'+$ts).slideToggle(400);
		return false;
	});
});
//activating an appropriate amount of starts based on users rating r
function star_rating(r) {
	document.write('<span class="star-active">');
	for(var i=0;i<5;i++){
		if (i==r) {
			document.write('</span><span class="star-inactive">');
		}
		document.write('★');
	}
	document.write('</span>');
}
//adjust the number of reviews and display appropriate info
function star_reviews(r, nr, id) {
	if (nr == 0) {
		document.write("No reviews");
	} else {
		star_rating(r);
		document.write(' &emsp; <a href="#" onclick="javascript:document.getElementById(\'h\').value=\'' + id + '\'; document.p.submit();">' + nr + ' review');
		if (nr > 1) { document.write('s'); }
		document.write('</a>');
	}
}


