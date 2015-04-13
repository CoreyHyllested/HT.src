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

mydropzone.on("successmultiple", function(file) {
	$(".dropzone-wrapper").find("div.img-delete").hide();
	$(".dropzone-status").html("<span class='success'>Images successfully uploaded!</span>");
	$("#multipleUploadContinueButton").show();
	$("#multipleUploadButton").hide();
	$("#lessonSave").html("Save").css("color","#1488CC");
});

$('button.multipleUploadButton').attr("disabled", true);

mydropzone.on("addedfile", function(file) {
	this.options.autoProcessQueue = false;
	$(".dropzone-status").empty();
	$('button.multipleUploadButton').attr("disabled", false).css("opacity", 1);
	$("#multipleUploadContinueButton").hide();
	$("#multipleUploadButton").show();	
});

mydropzone.on("processing", function() {
	$(".dropzone-status").html("Uploading Images - Please Wait...");
	this.options.autoProcessQueue = true;
});

$('button.multipleUploadButton').click(function() {
	mydropzone.processQueue();
});

// $(function() {
//     $(".dropzone").sortable({
//         items:'.dz-preview',
//         cursor: 'move',
//         opacity: 0.5,
//         containment: '.dropzone-wrapper',
//         distance: 20,
//         tolerance: 'pointer'
//     });
// })