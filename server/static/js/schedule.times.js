//update calculated times. so total calculated time is never negative

function formatNr(value) {
	value = value.toString();
	comma = ',';
	var reg = /(\d+)(\d{3})/;
	while (reg.test(value)) {
		value = value.replace(reg, '$1' + comma + '$2');
	}
	return value;
}

function update_time_diff(price) { 
  var start_val = document.getElementById("newslot_starttime").value;
  var start_hrs = parseInt(start_val[0]+start_val[1]);
  var start_min = parseInt(start_val[3]);
  var end_val = document.getElementById("newslot_endtime").value;
  var end_hrs = parseInt(end_val[0]+end_val[1]);
  var end_min = parseInt(end_val[3]);
  start_hrs = end_hrs - start_hrs;
  start_min = end_min - start_min;
  //check if we subtracted half an hour from a full hour
  //so we can adjust the hour duration by 1
  if (start_min == -3) {
    start_hrs -= 1;
    start_min = 3;
  }

  //now calculate the difference between starting and ending date
  var timeDiff = 0;
  /* assume same day....
  if (document.getElementById("datepicker").value != "") {
    var d1 = new Date(document.getElementById("datepicker").value);
    var d2 = new Date(document.getElementById("datepicker1").value);
    timeDiff = (d2.getTime() - d1.getTime())/(1000*60*60);
  } */

  //same day appointments
  if (start_hrs < 0 && timeDiff == 0 || isNaN(start_hrs) == true ) {
      document.getElementById("newslot_endtime").value = document.getElementById("newslot_starttime").value;
      document.getElementById("newslot_price").innerHTML = "$ ... ";
      document.getElementById("newslot-duration").innerHTML = "Update end time.";
  } else {
  	  //appointments within multiple days

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
	  //calculate the total timeslot price
	  var total = price * start_hrs;
	  if (start_min == 3) {
  	  	total += 0.5 * price;
	  }
	  //write it to the appropriate element on the page
	  document.getElementById("newslot_price").innerHTML = "$" + formatNr(total);
	  document.getElementById("newslot_price").value = formatNr(total);
  };
};
