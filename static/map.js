var init_x = (0).toString(10);
var init_y = (0).toString(10);
var selected = null;

function init() {
	document.getElementById('ward_map').contentDocument.documentElement.style.setProperty('--x_init', init_x);
	document.getElementById('ward_map').contentDocument.documentElement.style.setProperty('--y_init', init_y);
	var polys = document.getElementById('ward_map').contentDocument.getElementsByClassName('ward');
	var ward_map = document.getElementById('ward_map').contentDocument.getElementById('borough');
	ward_map.style.setProperty('transform', 'translate(' + init_x + 'px' + ',' + init_y + 'px)');
	calculate_colour_val();
}

function calculate_colour_val() {
    var wards = document.getElementsByClassName('area_box');
    console.log(wards.length);
    for (i = 0; i < wards.length; i++) {
        var ward_id = wards[i].classList.item(1);
        var score = parseFloat(wards[i].getElementsByClassName('score')[0].innerHTML);
        var colour_val = (255.0 / ( 1.0 + Math.exp( (score - 70.0) * -0.2 ) ) ).toString();
        var new_id = "ward" + " " + ward_id;
        var ward_poly = document.getElementById('ward_map').contentDocument.documentElement.getElementsByClassName(new_id);

        if (ward_poly.length == 1) {
            if (score != -1) {
            ward_poly[0].style.fill = "rgb(0, 0, " + colour_val + ")";
            }
            else {
                ward_poly[0].style.fill = "lightgrey";
            }
        }
    }
}

function get_mid(ward_id, score) {
	var mapDoc = document.getElementById('ward_map').contentDocument.documentElement;
	var poly_id = mapDoc.getElementsByClassName("ward" + " " + ward_id)[0];
	var SCALE = 2;
    var viewBounds = mapDoc.getBoundingClientRect();
	var viewportwidth = viewBounds.x + 0.5 * viewBounds.width;
	var viewportheight = viewBounds.y + 0.5 * viewBounds.height;
	//var viewportwidth = viewBounds.x + (0.5 * 590);
	//var viewportheight = (viewBounds.y + 60) + (0.5 * 340);
	//var view = mapDoc.getAttribute('viewBox');
	//console.log(view);

    var bounds = poly_id.getBoundingClientRect();
	var c_x = bounds.x + 0.5 * bounds.width; // centre x of polygon
	var c_y = bounds.y + 0.5 * bounds.height; // centre y of polygon
	console.log(viewportwidth, viewportheight);
	console.log(c_x, c_y);

    var t_x = (viewportwidth - (SCALE * c_x)).toString(10);
    var t_y = (viewportheight  - (SCALE * c_y)).toString(10);
    //mapDoc.getElementById('borough').classList.remove('wardMove');
    mapDoc.style.setProperty('--x', t_x);
    mapDoc.style.setProperty('--y', t_y);
    mapDoc.getElementById('borough').classList.add('wardMove');
    var blaa = mapDoc.getElementsByClassName('ward');
    for (i = 0; i < blaa.length; i++) {
        if (blaa[i].classList[1] != poly_id.classList[1]) {
            blaa[i].classList.toggle('ward_fade');
        }
    }
}