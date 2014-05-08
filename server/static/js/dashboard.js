// Script #1
// Removed - no datepicker2 stuff. 

// Script #2

//var jq = $.noConflict();
$("#today_button").click(function() {
	var today = moment().format("dddd, MMM D, YYYY");
	$("#datepicker2").datepicker('setDate', today);
	document.getElementById("header").innerHTML = today;
    var c = {{ts_appt|length}};
	for (var i = 1; i < c + 1; i++){
      if (document.getElementById("day-"+i).innerHTML != today){
        document.getElementById(i).style.display = 'none';
        document.getElementById("slot-expand-"+i).style.display = 'none';
      }
      else {
      	document.getElementById(i).style.display = 'block';
      }
	};
});

$(function() {
	//ensure enter doesn't submit form
    $("form[name=newts]").bind("keypress", function (e) {
        if (e.keyCode == 13) {
            return false;
        }
    });

	$("#to-profile-wrap").click(function () {
		var fd = new FormData();
		fd.append('hero', '{{bp.prof_id}}');
		console.log('profile-wrap', '{{bp.prof_id}}');

		var xhr = new XMLHttpRequest();
		xhr.open('post', "/profile", true);
		xhr.send(fd);

		xhr.onreadystatechange = function(e) {
			if (4 == this.readyState) {
				if (this.status == 200) {
					console.log(['xhr post complete ', e]);
					document.write(xhr.responseText);
				} else if (this.status == 500) {
					console.log(xhr.responseText);
					msg = JSON.parse(xhr.responseText);
					openAlertWindow('Uh oh!\n' + msg['usrmsg']);
				}
			}
		}
    	return false;
	});
});



// Script #3

google.maps.event.addDomListener(window, 'load', initialize);
document.getElementById("header").innerHTML = moment().format("dddd, MMM D, YYYY");
window.onload = function() {
  var today = new Date();
  today.setDate(today.getDate()-1);
  var c = {{timeslots|length}};
  for (var i = 1; i < c + 1; i++){
  	var date = new Date(document.getElementById("day-"+i).innerHTML);
  	var diff = today - date;
    if (today - date > 0){
      document.getElementById(i).style.display = 'none';
      document.getElementById("slot-expand-"+i).style.display = 'none';
    }
  };
}



// Script #4

$(function () {

   $('.request-wrap').click(function () {
        var id = this.id;
        var ch = $(this).attr("ch");
        var idx = $(this).attr("idx");
        var csrf = "{{ csrf_token() }}";
		var sid = "#appt-" + idx;

        var fd = new FormData();
        fd.append('appt_id', id);
        fd.append('appt_stat', 'cancel');
        fd.append('appt_challenge', ch);

        var xhr = new XMLHttpRequest();
        xhr.open('post', "/appointment/cancel", true);
        xhr.setRequestHeader("X-CSRFToken", csrf);
        xhr.send(fd);

        //catch response.  make any modificaitons.
        xhr.onreadystatechange = function(e) {
            if (4 == this.readyState) {
                if (this.status == 200) {
                    console.log(['xhr post complete ', e]);
                    console.log(xhr.responseText);
					$(sid).remove();
					msg = JSON.parse(xhr.responseText);
					openAlertWindow('Success.\n' + msg['usrmsg']);
                } else if (this.status == 400) {
                    console.log(['xhr post complete, err=500 ', e]);
                    openAlertWindow('Failure: ' + msg['usrmsg']);
                } else if (this.status == 500) {
                    console.log(['xhr post complete, err=500 ', e]);
                    openAlertWindow('Failure: ' + msg['usrmsg']);
                } else if (this.status == 501) {
                    console.log(['xhr post complete, err=501 ', e]);
                    msg = JSON.parse(xhr.responseText);
                    openAlertWindow('Failure: ' + msg['usrmsg']);
                } else {
                    console.log(['xhr post complete, err=?? ', this.status,  e]);
                    openAlertWindow('Failure: ' + msg['usrmsg']);
                }
            }
        };

        return false;
    });

   $('.reject-wrap').click(function () {
        var id = this.id;
        var ch = $(this).attr("ch");
        var idx = $(this).attr("idx");
        var csrf = "{{ csrf_token() }}";
		var sid = "#prop-" + idx;

        //console.log(['this is get started', id]);
        //console.log('this is get started ' +  ch);

        var fd = new FormData();
        fd.append('proposal_id', id);
        fd.append('proposal_stat', 'reject');
        fd.append('proposal_challenge', ch);

        var xhr = new XMLHttpRequest();
        xhr.open('post', "/proposal/reject", true);
        xhr.setRequestHeader("X-CSRFToken", csrf);
        xhr.send(fd);

        //catch response.  make any modificaitons.
        xhr.onreadystatechange = function(e) {
            if (4 == this.readyState) {
				msg = JSON.parse(xhr.responseText);
                if (this.status == 200) {
                    console.log(['xhr post complete ', e]);
                    console.log(xhr.responseText);
					openAlertWindow('Success.\n' + msg['usrmsg']);
					$(sid).remove();
                } else if (this.status == 500) {
                    console.log(['xhr post complete, err=500 ', e]);
                    openAlertWindow('Failure: ' + msg['usrmsg']);
                } else if (this.status == 501) {
                    console.log(['xhr post complete, err=501 ', e]);
                    openAlertWindow('Failure: ' + msg['usrmsg']);
                } else {
                    console.log(['xhr post complete, err=?? ', this.status,  e]);
                    openAlertWindow('Failure: ' + msg['usrmsg']);
                }
            }
        };

        return false;
    });

    $('.accept-wrap').click(function () {
		var id = this.id;
		var ch = $(this).attr("ch");
		var csrf = "{{ csrf_token() }}";

        console.log(['this is get started', id]);
        console.log('this is get started ' +  ch);

        var fd = new FormData();
		//matches ProposalActionForm
        fd.append('proposal_id', id);
        fd.append('proposal_stat', 'accept');
		fd.append('proposal_challenge', ch);

        var xhr = new XMLHttpRequest();
        xhr.open('post', "/proposal/accept", true);
        xhr.setRequestHeader("X-CSRFToken", csrf)
        xhr.send(fd)

        //catch response.  make any modificaitons.
		xhr.onreadystatechange = function(e) {
			if (4 == this.readyState) {
				msg = JSON.parse(xhr.responseText);
                if (this.status == 200) {
                    console.log(['xhr post complete ', e]);
                    openAlertWindow('Success!\n' + msg['usrmsg']);
					document.write(xhr.responseText);
                } else if (this.status == 500) {
                    console.log(['xhr post complete, err=500 ', e]);
                    openAlertWindow('Failure 500: ' + msg['usrmsg']);
                } else if (this.status == 501) {
                    console.log(['xhr post complete, err=501 ', e]);
                    openAlertWindow('Failure 501: ' + msg['usrmsg']);
                } else {
                    console.log(['xhr post complete, err=?? ', this.status,  e]);
                    openAlertWindow('Failure: ' + this.status + ': ' + msg['usrmsg']);
                }
            }
        };

        return false;
    });

});
