$(function add_start_times() {
	$("#newslot_starttime").empty();
	for (var i=0;i<24;i++) { 
		if (i<10) {
			var opt00 = new Option("0" + i + ":00 AM", "0"+i+":00 AM");
			var opt30 = new Option("0" + i + ":30 AM", "0"+i+":30 AM");
		} else if (i<12) {
			var opt00 = new Option(i + ":00 AM", i+":00 AM");
			var opt30 = new Option(i + ":30 AM", i+":30 AM");
		} else {
			var opt00 = new Option(i + ":00 PM", i+":00 PM");
			var opt30 = new Option(i + ":30 PM", i+":30 PM");
		}
		var nts_list=document.getElementById("newslot_starttime");
		nts_list.appendChild(opt00);
		nts_list.appendChild(opt30);
	}
	document.getElementById("newslot_starttime").value = "09:00 AM"
});

$(function add_end_times() {
	$("#newslot_endtime").empty();
	for (var i=0;i<24;i++) { 
		if (i<10) {
			var opt00 = new Option("0" + i + ":00 AM", "0"+i+":00 AM");
			var opt30 = new Option("0" + i + ":30 AM", "0"+i+":30 AM");
		} else if (i<12) {
			var opt00 = new Option(i + ":00 AM", i+":00 AM");
			var opt30 = new Option(i + ":30 AM", i+":30 AM");
		} else {
			var opt00 = new Option(i + ":00 PM", i+":00 PM");
			var opt30 = new Option(i + ":30 PM", i+":30 PM");
		}
		var nts_list=document.getElementById("newslot_endtime");
		nts_list.appendChild(opt00);
		nts_list.appendChild(opt30);
	}
	document.getElementById("newslot_endtime").value = "10:00 AM"
});

function update_time_diff(price) { 
  var start_val = document.getElementById("newslot_starttime").value;
  var start_hrs = parseInt(start_val[0]+start_val[1]);
  var start_min = parseInt(start_val[3]);
  var end_val = document.getElementById("newslot_endtime").value;
  var end_hrs = parseInt(end_val[0]+end_val[1]);
  var end_min = parseInt(end_val[3]);
  start_hrs = end_hrs - start_hrs;
  start_min = end_min - start_min;
  if (start_min == -3) {
    start_hrs -= 1;
    start_min = 3;
  }
  var timeDiff = 0;
  if (document.getElementById("datepicker").value != "") {
    var d1 = new Date(document.getElementById("datepicker").value);
    var d2 = new Date(document.getElementById("datepicker1").value);
    timeDiff = (d2.getTime() - d1.getTime())/(1000*60*60);
  }
  if (start_hrs < 0 && timeDiff == 0) {
      document.getElementById("newslot_endtime").value = document.getElementById("newslot_starttime").value;
      document.getElementById("newslot_price").value = 0;
      document.getElementById("newslot-duration").innerHTML = "";
  } else {
  	  start_hrs += timeDiff;
	  var toReturn = "";
	  if (start_hrs > 1) {
	    toReturn += start_hrs + " hours ";
	  }
	  if (start_hrs == 1) {
		toReturn += "1 hour "; 
	  }
	  if (start_min == 3) {
        document.getElementById("newslot-duration").innerHTML = toReturn + "30 minutes";
	  } else {
		document.getElementById("newslot-duration").innerHTML = toReturn;
	  }
	  var total = price * start_hrs;
	  if (start_min == 3) {
  	  	total += 0.5 * price;
	  }
	  document.getElementById("newslot_price").value = format(total);
  };
};
