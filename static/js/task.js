var DEBUG = true;
var sketchpad = null;

function closeModal() {
	$(".modal").modal("hide");
}

function toggleModal(text) {
	$("#infoModal-text").html(text);
	$("#infoModal").modal("show");
}

function updateProgressBar(currentPhase, numPhases, stimIdx, stimsLength) {
	var percentComplete = Math.round(stimIdx / stimsLength * 100);
	$("#progress-bar").attr("aria-valuenow", percentComplete);
	$("#progress-bar").attr("style", "width: " + percentComplete + "%");
	var phase = currentPhase.split("_")[1];
	$("#currentPhase").html(phase + "/" + numPhases);
	$("#progress-bar").text(percentComplete + "%");
}

function RenderUI(phaseConfig) {
	var UIComponents = phaseConfig['ui_components'];

	// Turn everything off first
	$("#user-input-col").hide();
	$("#descriptions-container").hide();
	$("#editor-container").hide();
	$("#stim-container").hide();
	$("#describe-container").css("visibility", "hidden");

	var dataDisplay = null;
	
	if (phaseConfig['sampling']) {
		if (UIComponents.indexOf("draw") > -1) {
			$("#editor-heading").text("Draw a new image like the ones you've seen")
			if (UIComponents.indexOf("describe") > -1) {
				$("#describe-container").css("visibility", "visible");
				$("#describe-heading").text("Describe your drawing");		
			}
		} else if (UIComponents.indexOf("describe") > -1) {
			$("#describe-heading").text("Describe a new image like the ones you've seen")
		} 
	} 
	
	// turn on relevant components
	for (i=0; i < UIComponents.length; i++) {
		var component = UIComponents[i];
		if (component === "draw") {
			// Create sketchpad
			if (sketchpad == null) { 
				sketchpad = Raphael.sketchpad("editor", {
					width: 500,
					height: 500,
					border: "solid",
					editing: true
				});
			} 
			var pen = sketchpad.pen();
			pen.width(2);

			$("#editor-container").show();
			$("#user-input-col").show()
		} else if (component === "describe") {
			$("#describe-container").css("visibility", "visible");
			$("#user-input-col").show()
		} else if (component === "images") {
			$("#stim-container").show();
			dataDisplay = "images";	// Update data display 
		} else if (component === "descriptions") {
			$("#descriptions-container").show();
			dataDisplay = "descriptions";	// Update data display
		}
	}
	
	return dataDisplay ? dataDisplay : "images";
}

function capitalize(string) {
	return string.charAt(0).toUpperCase() + string.slice(1);
}

function displayStim(phaseConfig, stimIndex) {
	if (phaseConfig['sampling']) { 
		return;
	}
	
	// Update images
	var path = "static/images/stim/" + phaseConfig['images'][stimIndex];
	$("#stim").prop("src", path);
	
	// Update descriptions if they exist
	if(phaseConfig['descriptions'] && phaseConfig['descriptions'].length > stimIndex) {
		$("#descriptions").html('"' + phaseConfig['descriptions'][stimIndex] + '"');	
	}
}

function getPhaseDescription(phaseConfig, phaseIndex) {
	var message = "<h1>Moving onto Phase " + phaseIndex + ":</h1>";
	message += "<p>In this phase, you will be:</p><ul>";

	if (phaseConfig["sampling"]) {
		message += "<li>Creating new drawings and descriptions. </li></ul> \
		<p>Remember, someone else will see these images. They should be able to verify that \
		they look similar to the other images you've seen.</p>";
	
		return message;
	}
	var UIComponents = phaseConfig['ui_components'];
	for (i=0; i < UIComponents.length; i++) {
		var component = UIComponents[i];
		if (component === "draw") {
			message += "<li>Copying images onto a sketchpad</li>";
		} else if (component === "describe") {
			message += "<li>Describing those images in text</li>"
		} else if (component === "images") {
			message += "<li>Looking at images </li>";	// Update data display 
		} else if (component === "descriptions") {
			message += "<li>Reading descriptions of images</li>";	// Update data display
		}
	}
	message += "</ul><p>Good luck!</p>"
	return message;
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
	var strokes = sketchpad ? sketchpad.json() : []
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
			if (DEBUG) {
				console.log(data);
			}

			const phases = data["phases"];
			var phaseIndex = 0;
			var numPhases = phases.length;
			var currentPhase = phases[phaseIndex];
			var phaseConfig = data[currentPhase];

			// Toggle UI Components
			var dataDisplay = RenderUI(phaseConfig);
			
			var stims = phaseConfig[dataDisplay];
			if (DEBUG) {
				console.log(stims);
			}
			var stimIndex = 0;

			displayStim(phaseConfig, stimIndex);
			updateProgressBar(currentPhase, numPhases, stimIndex, stims.length);

			$('#next-image').on('click', function nextDrawing() {

				// Rough heuristic to make sure the user has submitted appropriate data
				// Ideally the next button should be disabled until everything is filled correctly
				if (!DEBUG) {
					if (sketchpad && sketchpad.strokes().length < 2) {
						toggleModal("Please make sure you have accurately placed all your strokes on the sketchpad.");
						return;
					}
					if ($("#describe-container").css("visibility") === "visible" && !$("#describe").val()) {
						toggleModal("Please make sure you have entered an accurate description before moving on.");
						return;
					}
				}
				
				// Log data
				data = recordTrial(data, currentPhase);

				// Get next image
				stimIndex += 1;
				
				// Update progress bar
				updateProgressBar(currentPhase, numPhases, stimIndex, stims.length);

				// Check if we've hit the end of a phase
				if (stimIndex >= stims.length) {
					phaseIndex += 1;
					if (phaseIndex >= phases.length) {
						data["metadata"]["completed"] = true
						logData(data); 	// log that the user completed this experiment
						toggleModal("Experiment completed!");
						window.location.href = "feedback";	// Redirect to feedback form?

					} else {
						currentPhase = phases[phaseIndex];
						phaseConfig = data[currentPhase];
						var phase = currentPhase.split("_")[1];
						var message = getPhaseDescription(phaseConfig, phase);						
						toggleModal(message);
						dataDisplay = RenderUI(phaseConfig);
						stims = phaseConfig[dataDisplay];
						stimIndex = 0;
						updateProgressBar(currentPhase, numPhases, stimIndex, stims.length);
					}
				}
	
				// Reset Sketchpad and description
				$('#describe').val('');	
				if (sketchpad) {
					sketchpad.clear()
				}
				
				// Update stimulus
				displayStim(phaseConfig, stimIndex);
			});

		})
	.fail(function() {
		console.log('Failure!');
	});

});
