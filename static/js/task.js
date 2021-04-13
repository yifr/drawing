var sketchpad = null; 
var group_id = 1;
var stims= null;

function logStrokes() {
	console.log("User strokes: ");
	console.log(sketchpad.strokes());
}

if ($("#editor")) {
	sketchpad = Raphael.sketchpad("editor", {
		width: 400,
		height: 400,
		border: "solid",
		editing: true
	});

	var pen = sketchpad.pen();
	pen.width(2);
}

var easy = null;
var train = null;
var test = null;

$.get('get_stims', {'group_id': group_id})
	.done(function(data) {
		console.log(data)
		var all_stims = data;
		easy = all_stims[0];
		train = all_stims[1];
		test = all_stims[2];
		
		var max_train = easy.length + train.length;
		var max_test = test.length;
		stims = easy.concat(train).concat(test);
		console.log(stims)
		var stim = stims.shift();
		var path = 'static/images/stim/' + stim;
		$("#stim").prop("src", path);

		$("#erase-button").on('click', function() { 
			sketchpad.clear();
		});
		
		var idx = 1;
		var max_trials = max_train;
		var phase = "Train";
		$('#progress').html(phase + ": " + idx + "/" + max_trials);

		$('#next-image').on('click', function next_drawing() {
			// Get next image
			idx += 1;
			if (idx > max_trials) {
				phase = "Test";
				idx = 1;
				max_trials = max_test;
			}
			stim = stims.shift();
			console.log(stim)
			$('#progress').html(phase + ": " + idx + "/" + max_trials);
			path = 'static/images/stim/' + stim;
			$("#stim").prop('src', path);

			// Log strokes 
			logStrokes()
			$('#description').val('');	
			//Log Description
				
			// Reset Sketchpad and description
			if (sketchpad) {
				sketchpad.clear()
			}

		});

	});


