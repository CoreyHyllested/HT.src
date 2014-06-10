
Dropzone.autoDiscover = false;

mydropzone = new Dropzone("form.dropzone", 
	{ 
		url: '/upload',
		uploadMultiple: true,
		addRemoveLinks: true,
		maxFiles: 9,
		parallelUploads: 10,
		maxFileSize: 2,
		acceptedFiles: "image/*",
		autoProcessQueue: false,
		clickable: true
	}
);


mydropzone.on("errormultiple", function(file) {
	$(".dropzone-status").html("<span class='error'>Error Uploading Files</span>").fadeIn();
});

mydropzone.on("completemultiple", function(file) {
	$(".dropzone-status").html("<span class='success'>Images successfully uploaded! Returning to profile...</span>").fadeIn();
	setTimeout(function(){
	  $('form#dropzone-continue').submit();
	}, 2000);

});

mydropzone.on("addedfile", function(file) {

	var thisFileName = file.name;

	var dividerElement = Dropzone.createElement("<div>&nbsp;</div>");
	file.previewElement.appendChild(dividerElement);

	var captionInput = Dropzone.createElement("<input type='text' class='dz-image-caption' name='caption' maxlength='50' placeholder='Enter a caption' />");
	file.previewElement.appendChild(captionInput);
});

mydropzone.on("processing", function() {
	this.options.autoProcessQueue = true;
});

$('button.multiple-upload-button').click(function() {
	mydropzone.processQueue();
});


$(function() {
    $(".dropzone").sortable({
        items:'.dz-preview',
        cursor: 'move',
        opacity: 0.5,
        containment: '.dropzone-wrapper',
        distance: 20,
        tolerance: 'pointer'
    });
})