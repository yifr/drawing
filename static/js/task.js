var DEBUG = true;
var sketchpad = null;

function RenderUI(UI_Components) {
	// Turn everything off first
	$("#descriptions-container").hide();
	$("#editor-container").hide();
	$("#stim-container").hide();
	$("#describe-container").css("visibility", "hidden");

	var data_display = null;

	// turn on relevant components
	for (i=0; i < UI_Components.length; i++) {
		var component = UI_Components[i];
		if (component === "draw") {
			// Create sketchpad
			if (sketchpad == null) { 
				sketchpad = Raphael.sketchpad("editor", {
					width: 400,
					height: 400,
					border: "solid",
					editing: true
				});
			} 
			var pen = sketchpad.pen();
			pen.width(2);

			$("#editor-container").show();
		} else if (component === "describe") {
			$("#describe-container").css("visibility", "visible");
		} else if (component === "images") {
			$("#stim-container").show();
			data_display = "images";	// Update data display 
		} else if (component === "descriptions") {
			$("#descriptions-container").show();
			data_display = "descriptions";	// Update data display
		}
	}

	return data_display;
}

function capitalize(string) {
	return string.charAt(0).toUpperCase() + string.slice(1);
}

function displayStim(newStim, dataDisplay) {
	if (dataDisplay === "images") {
		var path = "static/images/stim/" + newStim;
		$("#stim").prop("src", path);
	} else if (dataDisplay === "descriptions") {
		$("#descriptions").text(newStim);	
	}
	return
}

function recordData() {
	var record = {};
	var strokes = [];
	if (sketchpad) {
		strokes = sketchpad.strokes()
	}
	if ($("
}

$(document).ready(function() { 
	console.log('Loaded page');
	$.get("experiment_config")
		.done(function(data) {
			console.log(data);

			const phases = data["phases"];
			var phaseIndex = 0;
			var currentTrial = phases[phaseIndex];
			var currentConfig = data[currentTrial];

			// Toggle UI Components
			var UIComponents = currentConfig['ui_components'];
			var dataDisplay = RenderUI(UIComponents);

			var stims = currentConfig[dataDisplay];
			var stimIndex = 0;
			console.log(stims)
			
			displayStim(stims[stimIndex], dataDisplay);
			$('#progress').html(capitalize(currentTrial) + ": " + (stimIndex + 1) + "/" + stims.length);

			$('#next-image').on('click', function nextDrawing() {
				if (!DEBUG) {
					if (sketchpad && sketchpad.strokes().length < 2) {
						alert("Please make sure you have accurately placed all your strokes on the sketchpad.");
						return;
					}
					if ($("#describe-container").css("visibility") === "visible" && !$("#describe").text()) {
						alert("Please make sure you have entered an accurate description before moving on.");
						return;
					}
				}
				
				// Log data
				var trialData = recordData();

				// Get next image
				stimIndex += 1;
				if (stimIndex >= stims.length) {
					phaseIndex += 1;
					if (phaseIndex >= phases.length) {
						alert("Experiment completed!");
						return
						// Redirect to something else
					} else {
						currentTrial = phases[phaseIndex];
						currentConfig = data[currentTrial];
						alert("Moving onto the " + currentTrial + " phase!");
						UIComponents = currentConfig['ui_components'];
						dataDisplay = RenderUI(UIComponents);
						stims = currentConfig[dataDisplay];
						stimIndex = 0;
					}
				}

				$('#progress').html(capitalize(currentTrial) + ": " + (stimIndex + 1) + "/" + stims.length);
				
				stim = stims[stimIndex];
				displayStim(stim, dataDisplay);

					

				// Reset Sketchpad and description
				$('#description').val('');	
				if (sketchpad) {
					sketchpad.clear()
				}

			});

		})
	.fail(function() {
		console.log('Failure!');
	});

});
