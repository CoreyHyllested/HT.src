Dropzone.autoDiscover = false;

mydropzone = new Dropzone("form.dropzone", 
	{ 
		url: '/upload',
		uploadMultiple: true,
		addRemoveLinks: true,
		maxFiles: 32,
		parallelUploads: 10,
		maxFileSize: 2,
		acceptedFiles: "image/*",
		autoProcessQueue: false,
		clickable: true
	}
);

mydropzone.on("maxfilesreached", function(file) {
	$(".dropzone-status").html("<span>You have reached the maximum number of files allowed (32).</span>");
});

mydropzone.on("maxfilesexceeded", function(file) {
	$(".dropzone-status").html("<span class='error'>You have exceeded the maximum number of files allowed (32).</span>");
});

mydropzone.on("error", function(file, errorMessage) {
	$(".dropzone-status").html("<span class='error'>Error Encountered: "+errorMessage+"</span>");
});

// mydropzone.on("complete", function(file) {
// 	mydropzone.on("error", function(file) {
// 		$(".dropzone-status").html("<span class='error'>Upload Error Encountered.</span>");
// 	});	
// 	$
// });

mydropzone.on("successmultiple", function(file) {

	$(".dropzone-status").html("<span class='success'>Images successfully uploaded! Continuing ... </span>");
	setTimeout(function(){
	  $('form#dropzone-continue').submit();
	}, 2000);

});

// Keeping this here for reference in case we want to add custom elements to the image preview thumbnails:
// mydropzone.on("addedfile", function(file) {

//     // Create the remove button
//     var removeButton = Dropzone.createElement("<div class='img-delete'>×</div>");

// 	var headerElement = Dropzone.createElement("<div class='header'><div class='img-delete'>×</div></div>");

//     // Capture the Dropzone instance as closure.
//     var _this = this;

//     // Listen to the click event
//     headerElement.addEventListener("click", function(e) {
//       // Make sure the button click doesn't submit the form:
//       e.preventDefault();
//       e.stopPropagation();

//       // Remove the file preview.
//       _this.removeFile(file);
//       // If you want to the delete the file on the server as well,
//       // you can do the AJAX request here.
//     });

//     file.previewElement.insertBefore(headerElement, file.previewElement.firstChild);
// });


$('button.multipleUploadButton').attr("disabled", true);

mydropzone.on("addedfile", function(file) {
	$('button.multipleUploadButton').attr("disabled", false);
});

mydropzone.on("processing", function() {
	this.options.autoProcessQueue = true;
});

$('button.multipleUploadButton').click(function() {
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