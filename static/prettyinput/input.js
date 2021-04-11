
/*
10-04-2021
valtert
VALTER YDE DAUGBERG

<div class="pretty-input" id="prettyInput1">Din mor</div>
add a ! for secret
*/


// ********* functions *********
function init() {

	var inputs = document.getElementsByClassName('pretty-input')
	var ihtml, input, type = 'text';
	for (var i = 0; i < inputs.length; i++) {
		ihtml = '';
		input = inputs[i];

		if (input.innerHTML.indexOf('!') >= 0) {
			type = 'password';
		} 

		ihtml += '<input name="'+ input.id +'" id="input-'+input.id+'" type="'+type+'" class="pretty-input-input"/>';
		ihtml += '<p class="pretty-input-placeholder">'+input.innerHTML.replaceAll('!','')+'</p>';
		input.innerHTML = ihtml;
	}
}

function fixPasswordRemember () {
	setTimeout(() => {

		inputs = document.getElementsByClassName('pretty-input-input');
		for (var i = 0; i < inputs.length; i++) {
			if (inputs[i].value.length > 0) {

				$(inputs[i].nextSibling).animate({
					top: '5%',
					'font-size': '1rem',
					'left': '2%',
				}, 'fast');
			}
		}
	}, 50);
}



// ********* init *********
init()

// ********* event handlers *********
$('.pretty-input').click( (result) => {
	$(result.currentTarget.childNodes[0]).focus()
})

$('.pretty-input-input').on('focus', (result) => {
	$(result.target.nextSibling).animate({
		top: '5%',
		'font-size': '1rem',
		'left': '2%',
	}, 'fast');
})

$('.pretty-input').focusout((result) => {
	if (result.currentTarget.childNodes[0].value == '') {
		$(result.currentTarget.childNodes[1]).animate({
			top: '50%',
			'font-size': '100%',
			'left': '4%',
		}, 'fast');
	}
});

// ********* hotfix *********
fixPasswordRemember()