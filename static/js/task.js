var DEBUG = false;
var sketchpad = null;

function closeModal() {
	$(".modal").modal("hide");
}

function toggleModal(text) {
	$("#infoModal-text").html(text);
	$("#infoModal").modal("show");
}

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
}

function logData(data) {
	$.ajax({
		type: "POST",
		url: "record_data", 
		contentType: "application/json; charset=utf-8",
		data: JSON.stringify(data)
	})
	.done(function(response) {
		message = response['message']
		console.log(response);
	})
}

function recordTrial(data, phase) {
	// Make sure data has keys 
	if (!("strokes" in data[phase])) {
		data[phase]["strokes"] = [];	
		data[phase]["user_descriptions"] = [];
	}
	
	// Get strokes and user descriptions
	var strokes = sketchpad ? sketchpad.strokes() : []
	data[phase]["strokes"].push(strokes);
	var userDescription = $("#describe").val();
	data[phase]["user_descriptions"].push(userDescription);	
	logData(data);

	return data;
}

$(document).ready(function() { 
	console.log('Loaded page');
	$.get("experiment_config")
		.done(function(data) {
			console.log(data);

			const phases = data["phases"];
			var phaseIndex = 0;
			var currentPhase = phases[phaseIndex];
			var phaseConfig = data[currentPhase];

			// Toggle UI Components
			var UIComponents = phaseConfig['ui_components'];
			var dataDisplay = RenderUI(UIComponents);

			var stims = phaseConfig[dataDisplay];
			var stimIndex = 0;

			if (DEBUG) { 
				console.log(stims)
			}
			
			displayStim(stims[stimIndex], dataDisplay);
			$('#progress').html(capitalize(currentPhase) + ": " + (stimIndex + 1) + "/" + stims.length);

			$('#next-image').on('click', function nextDrawing() {

				// Rough heuristic to make sure the user has submitted appropriate data
				// Ideally the next button should be disabled until everything is filled correctly
				if (!DEBUG) {
					if (sketchpad && sketchpad.strokes().length < 2) {
						toggleModal("Please make sure you have accurately placed all your strokes on the sketchpad.");
						return;
					}
					if ($("#describe-container").css("visibility") === "visible" && !$("#describe").text()) {
						toggleModal("Please make sure you have entered an accurate description before moving on.");
						return;
					}
				}
				
				// Log data
				data = recordTrial(data, currentPhase);

				// Get next image
				stimIndex += 1;

				// Check if we've hit the end of a phase
				if (stimIndex >= stims.length) {
					phaseIndex += 1;
					if (phaseIndex >= phases.length) {
						data['meta']['completed'] = True
						logData(data); 	// log that the user completed this experiment
						toggleModal("Experiment completed!");
						return;	// Redirect to feedback form?

					} else {
						currentPhase = phases[phaseIndex];
						phaseConfig = data[currentPhase];
						toggleModal("Moving onto the " + currentPhase + " phase!");
						UIComponents = phaseConfig['ui_components'];
						dataDisplay = RenderUI(UIComponents);
						stims = phaseConfig[dataDisplay];
						stimIndex = 0;
					}
				}

				// Update progress bar
				$('#progress').html(capitalize(currentPhase) + ": " + (stimIndex + 1) + "/" + stims.length);
				
				// Reset Sketchpad and description
				$('#description').val('');	
				if (sketchpad) {
					sketchpad.clear()
				}
				
				// Update stimulus
				stim = stims[stimIndex];
				displayStim(stim, dataDisplay);
			});

		})
	.fail(function() {
		console.log('Failure!');
	});

});
