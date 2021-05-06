var DEBUG = false;
var sketchpad = null;
var nextButtonTimer = false;

function closeModal() {
	$(".modal").modal("hide");
}

function toggleModal(text) {
	$("#infoModal-text").html(text);
	$("#infoModal").modal("show");
}

function replay() {
	sketchpad.animate();
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
				sketchpad = Raphael.sketchpad("viewer", {
					width: 500,
					height: 500,
					border: "solid",
					editing: false
				});
			} 
			var pen = sketchpad.pen();
			pen.width(2);

			$("#editor-container").show();
			$("#user-input-col").show()
		} else if (component === "describe") {
			$("#describe-container").css("visibility", "visible");
		} else if (component === "images") {
			$("#stim-container").show();
			dataDisplay = "images";	// Update data display 
			if (UIComponents.indexOf("draw") < 0 && UIComponents.indexOf("describe") < 0) {
				nextButtonTimer = true;
			}
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

	
	// Update images
	var path = "static/images/stim/" + phaseConfig['images'][stimIndex];
	$("#stim").prop("src", path);
	if (sketchpad) {
		sketchpad.json(phaseConfig['strokes'][stimIndex]);
		sketchpad.animate();
	}

	if (phaseConfig['user_descriptions']) {
		$("#describe").text(phaseConfig['user_descriptions'][stimIndex]);
	}

	// Update descriptions if they exist
	if(phaseConfig['descriptions'] && phaseConfig['descriptions'].length > stimIndex) {
		$("#descriptions").html('"' + phaseConfig['descriptions'][stimIndex] + '"');	
	}

	if (nextButtonTimer) {
		$("#next-image").prop("disabled", true);
		setTimeout(function(){
			$("#next-image").prop("disabled", false);
		}, 3000);
	}
}

function getPhaseDescription(phaseConfig, phaseIndex) {
	var message = "<h1>Beginning Phase " + phaseIndex + ":</h1>";
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

$(document).ready(function() { 
	console.log('Loaded page');
	$.get("user_results")
		.done(function(data) {
			if (DEBUG) {
				console.log(data);
			}

			const phases = data["phases"];
			var phaseIndex = 0;
			var numPhases = phases.length;
			var currentPhase = phases[phaseIndex];
			var phaseConfig = data[currentPhase];

			// Toggle UI Components and explain phase
			var dataDisplay = RenderUI(phaseConfig);
			// var message = getPhaseDescription(phaseConfig, currentPhase.split('_')[1]);						
			// toggleModal(message);
			
			var stims = phaseConfig[dataDisplay];
			if (DEBUG) {
				console.log(stims);
			}
			var stimIndex = 0;

			displayStim(phaseConfig, stimIndex);
			updateProgressBar(currentPhase, numPhases, stimIndex, stims.length);

			$('#next-image').on('click', function nextDrawing() {

				// Get next image
				stimIndex += 1;
				
				// Update progress bar
				updateProgressBar(currentPhase, numPhases, stimIndex, stims.length);

				// Check if we've hit the end of a phase
				if (stimIndex >= stims.length) {
					phaseIndex += 1;
					if (phaseIndex >= phases.length) {
						data["metadata"]["completed"] = true
						toggleModal("Experiment completed!");

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
				$('#describe').text('');	
				if (sketchpad) {
					sketchpad.clear()
				}
				
				// Update stimulus
				displayStim(phaseConfig, stimIndex);
			});


			$('#previous-image').on('click', function previousDrawing() {

				// Get next image
				stimIndex = Math.max(stimIndex - 1, 0);
				
				// Update progress bar
				updateProgressBar(currentPhase, numPhases, stimIndex, stims.length);

				// Check if we've hit the end of a phase
				if (stimIndex < 0) {
					phaseIndex = Math.max(phaseIndex - 1, 0);
					if (phaseIndex >= phases.length) {
						data["metadata"]["completed"] = true
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
				$('#describe').text('');	
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
