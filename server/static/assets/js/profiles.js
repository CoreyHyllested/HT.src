var profile_version = 0.02;

function referral_update(e)	{ window.location.href='/referral/' + $(e).data('ref-id') + '?edit=true'; }
function referral_delete(e) {
	rid = $(e).data('ref-id');
	$.ajax({	url		: '/api/referral/' + rid + '/destroy',
				type	: 'DELETE',
				success : function(data) {
					referrals = $('article.referral');
					$(referrals).each(function(idx, referral)  {
						if ($(referral).data('ref-id') === rid) {
							$(referral).remove();
						}
					});
				},
				error	: function(data) {
					console.log("AJAX Error", data);
				}
	});
	return false;
}



$(document).ready(function () {
	if (typeof debug === 'boolean') console.log('profile.js: v' + profile_version);
	$('div.ref-actions').on('click', '.btn-referral-delete',	function () { referral_delete(this);	});
	$('div.ref-actions').on('click', '.btn-referral-update',	function () { referral_update(this);	});
});
