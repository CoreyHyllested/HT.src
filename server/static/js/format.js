//checking if the key currently typed in is a number
function isNumberKey(evt) {
  var charCode = (evt.which) ? evt.which : event.keyCode;
  if (charCode > 31 && (charCode < 48 || charCode > 57) && charCode != 46)
    return false;
  else {
    var input = document.getElementById("newslot_price").value;
    var len = document.getElementById("newslot_price").value.length;
    var index = document.getElementById("newslot_price").value.indexOf('.'); 

    //checking if the current value is a decimal number and whether we
    //will allow a dot in this field
    if (index > 0 && charCode == 46) { 
      return false; 
    } 
    if (index >0 || index==0) {
      var CharAfterdot = (len + 1) - index; 
      if (CharAfterdot > 3) { 
        return false; 
      } 
    }

    if (charCode == 46 && input.split('.').length >1) {
        return false;
    }
  }
  return true; 
}

//formating a large number to have a thousand separator
function format(value) {
	value = value.toString();
  comma = ',';
  var reg = /(\d+)(\d{3})/;
  while (reg.test(value)) {
    value = value.replace(reg, '$1' + comma + '$2');
  }
  return value;
}