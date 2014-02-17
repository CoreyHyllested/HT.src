function isNumberKey(evt) {
  var charCode = (evt.which) ? evt.which : event.keyCode;
  if (charCode > 31 && (charCode < 48 || charCode > 57))
    return false;
  return true;
};

function format(value) {
	value = value.toString();
  comma = ',';
  var reg = /(\d+)(\d{3})/;
  while (reg.test(value)) {
    value = value.replace(reg, '$1' + comma + '$2');
  }
  return value;
}