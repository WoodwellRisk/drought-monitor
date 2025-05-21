var forecastMap = document.getElementById('forecast_map');
console.log(forecastMap)

function getMapZoom() {
    let forecastMap = document.querySelector('#forecast_map');
    forecastMap.on('plotly_event', function(){

    	console.log(forecastMap)

	});
}