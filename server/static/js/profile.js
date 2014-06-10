// Script #1

jQuery(function($) {
  $( "#datepicker" ).datepicker({
		  inline: true
	  });
});
jQuery(function($) {
  $( "#datepicker1" ).datepicker({
		  inline: true
	  });
});

jQuery(function($) {
	$('#datepicker').change(function() {
		var d1 = new Date(document.getElementById("datepicker").value);
		var d2 = new Date(document.getElementById("datepicker1").value);
		var timeDiff = d2.getTime() - d1.getTime();
		if (timeDiff < 0 || document.getElementById("datepicker1").value == "") {
			document.getElementById("datepicker1").value = document.getElementById("datepicker").value;
		}
		update_time_diff({{hp.prof_rate}});
	});
});

jQuery(function($) {
	$('#datepicker1').change(function() {
		var d1 = new Date(document.getElementById("datepicker").value);
		var d2 = new Date(document.getElementById("datepicker1").value);
		var timeDiff = d2.getTime() - d1.getTime();
		if (timeDiff < 0 || document.getElementById("datepicker").value == "") {
          document.getElementById("datepicker").value = document.getElementById("datepicker1").value;
		}
          update_time_diff({{hp.prof_rate}});
	});
});


// Script #2

var jq = $.noConflict();
//ensure enter doesn't submit form
$("form[name=newts]").bind("keypress", function (e) {
    if (e.keyCode == 13) {
        return false;
    }
});

google.maps.event.addDomListener(window, 'load', initialize);
document.getElementById("profile_price").innerHTML = "$" + format({{hp.prof_rate}});
document.getElementById("li_rate").innerHTML = "$" + format({{hp.prof_rate}}) + " / hour";
$('#newslot_starttime').change(function() {
	update_time_diff({{hp.prof_rate}});
});
$('#newslot_endtime').change(function() {
	update_time_diff({{hp.prof_rate}});
});
if (document.getElementById("datepicker") != null) {
	document.getElementById("datepicker").value = moment().format("dddd, MMM D, YYYY");
}
if (document.getElementById("datepicker1") != null) {
	document.getElementById("datepicker1").value = moment().format("dddd, MMM D, YYYY");
}
if (document.getElementById("newslot-label-rate") != null) {
	document.getElementById("newslot-label-rate").innerHTML = "This person's default rate is $" + format({{hp.prof_rate}}) + " / hour"
}
window.onload = function() {
  var today = new Date();
  today.setDate(today.getDate()-1);
};


// Script #3
$(document).ready(function() {


	$('#send_proposal').click(function() {
		$hero_acct = '{{hp.prof_id}}';
		$hero_name = '{{hp.prof_name}}';
		$cost = parseInt($('#newslot_price').val().replace(/,/g, ''), 10) * 100;
		$time = $('#newslot-duration').html();
		$desc = $('#newslot_description').val();
		$area = $('#newslot_location').val();
		$ts_d = $('#datepicker').val();
		$ts_h = $('#newslot_starttime').val();

		$tf_d = $('#datepicker1').val();
		$tf_h = $('#newslot_endtime').val();

		$bp_name = '{{bp.prof_name}}';
		$bp_id   = '{{bp.prof_id}}';
		console.log('hero_acct = ' + $hero_acct + ' ;' + $hero_name);
		console.log('ts = ' + $ts_d+ ' ; ' + $ts_h);
		console.log('tf = ' + $tf_d+ ' ; ' + $tf_h);
//			console.log('hero_cost = ' + $hero_cost + " asInt(" + $hc_1 + "); *100 =" + $hc_2 );
		console.log('@ cost = ' + $cost);
//			alert('Seller: ' + $hero_name + '\nSellID: ' + $hero_acct + '\n' + $time + ' @ $' + $cost + '\nMeet: ' + $area + '\nFor: ' + $desc + '\nBuyer:' + $bp_name);

		var srv_callback = function(res) {
			console.log('srv_callback is happening');
			console.log('time = ' + $time);
			console.log('cost = ' + $cost);

			/*
			$.each(res.card, function(key, element) {
				    console.log('res.' + key + ' = ' + element);
			});
			res.id = tok_3dAR0tkCHTAETp 
			res.livemode = false 
			res.created = 1394322237 
			res.used = false 
			res.object = token 
			res.type = card 
			res.card = [object Object] 
			res.email = corey.hyllested@gmail.com 
			
			[[res.card] == 
				res.card.id = card_3dAUcwyJebTMrO 
				res.card.id.object = card 
				res.last4 = 4242 
				res.type = Visa 
				res.exp_month = 8 
				res.exp_year = 2015 
				res.fingerprint = cOBLtIWQiyFZUGvf 
				res.customer = null 
				res.country = US 
				res.name = Corey Hyllested 
				res.address_line1 = Apartment T-331 
				res.address_line2 = null 
				res.address_city = Boulder 
				res.address_state = CO 
				res.address_zip = 80305 
				res.address_country = United States 
			]
			*/


			var $csrf = $('<input type=hidden name=csrf_token />').val("{{ csrf_token() }}");

		   	var $stripe_tokn = $('<input type=hidden name=stripe_tokn />').val(res.id);
		   	var $stripe_card = $('<input type=hidden name=stripe_card />').val(res.card.id);
		   	var $stripe_name = $('<input type=hidden name=stripe_name />').val(res.card.name);
		   	var $stripe_city = $('<input type=hidden name=stripe_city />').val(res.card.address_city);
		   	var $stripe_stat = $('<input type=hidden name=stripe_stat />').val(res.card.address_state);
		   	var $stripe_cust = $('<input type=hidden name=stripe_cust />').val(res.card.customer);
		   	var $stripe_fngr = $('<input type=hidden name=stripe_fngr />').val(res.card.fingerprint);
		   	var $stripe_mail = $('<input type=hidden name=stripe_mail />').val(res.email);

		   	var $prop_hero =  $('<input type=hidden name=prop_hero />').val($hero_acct);
		   	var $prop_cost =  $('<input type=hidden name=prop_cost />').val($cost);
		   	var $prop_area =  $('<input type=hidden name=prop_area />').val($area);
		   	var $prop_desc =  $('<input type=hidden name=prop_desc />').val($desc);

		   	var $prop_s_date =  $('<input type=hidden name=prop_s_date />').val($ts_d);
		   	var $prop_s_hour =  $('<input type=hidden name=prop_s_hour />').val($ts_h);
		   	var $prop_f_date =  $('<input type=hidden name=prop_f_date />').val($tf_d);
		   	var $prop_f_hour =  $('<input type=hidden name=prop_f_hour />').val($tf_h);
			
			$('form[name="charge"]').append($csrf);
			console.log('append stripe');
			$('form[name="charge"]').append($stripe_tokn).append($stripe_card).append($stripe_cust).append($stripe_fngr).append($stripe_mail);
			$('form[name="charge"]').append($prop_hero).append($prop_cost).append($prop_area).append($prop_desc);
			$('form[name="charge"]').append($prop_s_date).append($prop_s_hour);
			$('form[name="charge"]').append($prop_f_date).append($prop_f_hour);
			$('form[name="charge"]').submit();
		};

		/*$desc.substring(0,50)*/
		StripeCheckout.open({
			key: 'pk_test_ga4TT1XbUNDQ3cYo5moSP66n',
			amount:		 $cost,
			address:     true,
			description: 'You will not be charged until one day before the meeting', 
			name:		 $hero_name, 
			currency:	 'usd',
			panelLabel:	 'Checkout',
			token:		srv_callback
		});
		return false;
	});

});