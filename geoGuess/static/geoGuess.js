var guess_coordinates = [38.029305, -78.476677]
var answer_coordinates = [38.029305, -78.476677]


function initialize() {
    const defaultLocation = {lat: 38.029305, lng: -78.476677}; //can change location
    const map = new google.maps.Map(document.getElementById("map"), {
        center: defaultLocation,
        zoom: 14,
    });

    const marker = new google.maps.Marker({
        position: defaultLocation,
        visible: false, //made the marker view be initially false
        map,
    });

    const panorama = new google.maps.StreetViewPanorama(
        document.getElementById("pano"),
        {
            position: defaultLocation,
            pov: {
                heading: 34,
                pitch: 10,
            },
        }
    );

    map.addListener("click", (e) => {
        placeMarkerAndPanTo(e.latLng, map, marker);
    });
    //window.initialize = initialize;
}

window.initialize = initialize;

function placeMarkerAndPanTo(latLng, map, marker) {
    marker.visible = true;
    marker.setPosition(latLng);
    map.panTo(latLng);
    guess_coordinates[0] = latLng.lat();
    guess_coordinates[1] = latLng.lng();
}

function makeAGuess() {
    var guess = new google.maps.LatLng(guess_coordinates[0], guess_coordinates[1]);
    var answer = new google.maps.LatLng(answer_coordinates[0], answer_coordinates[1]);
    var distance = google.maps.geometry.spherical.computeDistanceBetween(guess, answer);
    document.getElementById("distance").innerHTML = "Your guess was " + (distance / 1000.0).toFixed(2) + " kilometers away from the correct spot!";
    //check distance, scoring
}

function getRandomNumber(from, to, fixed) {
    return (Math.random() * (to - from) + from).toFixed(fixed) * 1;
}

    