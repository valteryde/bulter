
Array.prototype.random = function(first_argument) {
	index = Math.floor(Math.random()*this.length)
	return this[index];
};

// helper function to erase color
// this may be a tad ineffecient. Maybe a data mark could be usefull?

// helper function to search for data in class
function searchForChild(ele, change) {
	for (var i = 0; i < ele.children.length; i++) {
		child = ele.children[i]
					
		for (var j = 0; j < child.classList.length; j++) {
			if (child.classList[j].slice(0,5) == 'data-') {
						
				child.style.background = change;
				break;
			}
		}
	}
}

function eraseColor() {
	for (var i = 1; i < 32; i++) {
		ele = document.getElementById('dt-'+i.toString());
		if (!ele) {
			break
		}
		ele.style.background = null;
		searchForChild(ele, null)
	}
}

// helper for two way for loop
function omnidirectionalForLoop(_1, _2, content) {

	if (_1 > _2) {
		temp = _1;
		_1 = _2-1;
		_2 = temp+1;
	}

	if (_1 == _2) {
		_1 -= 1;
		_2 += 1;
	}

	for (var i = _1; i < _2; i++) {
		content(i);
	}

}

// create modal for creation of event.
var data_end, data_start;
function openEventCreater(a, b) {
	$('#ChangeModal').modal('show');
	$('#friendInvite').focus();

	var d = new Date();
	var year = d.getFullYear();
	var month = d.getMonth()+1;

	if (month < 10) {
		month = '0' + month.toString() 
	}

	start = Math.min(parseFloat(a), parseFloat(b));
	if (start < 10) {
		start = '0' + start.toString();
	}
	start += '-' + month + '-' + year;		
	end = Math.max(parseFloat(a), parseFloat(b));
	if (end < 10) {
		end = '0' + end.toString();
	}
	end += '-' + month + '-' + year;
	data_start = start;
	data_end = end;

	$('#data-EventStart').html(start);
	$('#data-EventEnd').html(end);
}

// for the 2 presses.
var set = null;
function marker(target) {
	if (colorPickerLock) {
		set = null;
		eraseColor();
		return;
	}
	if (set) {
		openEventCreater(set, target.id.replace('out-', ''));
		set = null;

	} else {
		set = target.id.replace('out-', '');
		document.getElementById('dt-'+set.toString()).style.background = background;
		searchForChild(document.getElementById('dt-'+set.toString()), background)
	}
}
 
// display the "snake" of the event.
// fire on move.
var mousePos;
function displayPreview(e) {
	var ele;

	//mousePos = ?;
	var found = -1;
	if (!set) {
		return;
	}

	if (e.target.id.slice(0,3) != 'dt-') {
				
		for (var j = 0; j < e.target.classList.length; j++) {
					
			if (e.target.classList[j].slice(0,5) == 'data-') {
				found = j;
				break;
			}

		}
		if (found === -1) {
			return;
		}
	}
			
	if (found !== -1) {
		target = e.target.classList[found];
		targetNr = target.replace('data-', '');
	} else {
		target = e.target.id;
		targetNr = target.replace('dt-', '');
	}

	eraseColor()
	omnidirectionalForLoop(parseFloat(set), parseFloat(targetNr)+1, function(i)
			 {
		ele = document.getElementById('dt-'+(i).toString());
		ele.style.background = background;
		searchForChild(ele, background)
	})
}

function registerColors(day, event, nmOfClass) {

	if (days[day]) {
		days[day].push([event, nmOfClass]);
	} else {
		days[day] = [[event, nmOfClass]];
	}
	//proc = 1/days[day];
}

function sepEvents() {

	for (const i in days) {

		var wrap = document.getElementById('dt-'+i);

		for (var j = 0; j < days[i].length; j++) {
					
			div = document.createElement('div');
			div.classList.add('eventInCard')
			div.style.height = (1/days[i].length*100).toString()+'%';
			div.style.top = (j*1/days[i].length*100).toString()+'%';
			div.classList.add(days[i][j][1])
			div.classList.add('data-'+i)
			
			var eventData = days[i][j][0];
			div.innerHTML = '<p class="eventTextName">'+eventData.name+'</p>';
			div.innerHTML += '<p class="eventTextDesc">' + (eventData.ptp.slice(0,eventData.ptp.length-1).replaceAll('-', ', ')) + '</p>'

			wrap.appendChild(div);
		}
	}
}


function assignColor (month=4) {
			
	//console.log(events)
	/*

	create color for each events
	create classes for every person or group.
	(use ptp data)

	check if start date is in this month.
	hvis end er mindre end start så det en ny måned.
	og så viser vi ikke dem mere. Så bare break.

	*/

	var style = document.createElement('style');
	style.type = 'text/css';

	var ih = '';
	var classes = [];

	for (var i = 0; i < events.length; i++) {
		event = events[i]

		// get start to end.
		var startDate = parseFloat(event.start.split('-')[0]);
		var endDate = parseFloat(event.end.split('-')[0]);

		// edge case -- event spans full month.
		if (event.start.split('-')[1] < month && event.end.split('-')[1] > month) {
					
			startDate = 1;
			endDate = last;

		} else {

			// month check...
			if (event.start.split('-')[1] != month) {
					
				if (event.end.split('-')[1] == month) {
						
					startDate = 1;

				} else {
					continue
				}

			}
		}

		var nmOfClass = 'eve-'+event.ptp.replaceAll('-','');
		event.class = nmOfClass
				
		if (startDate > endDate) {
			endDate = 31;
		}

		for (var j = startDate; j < endDate+1; j++) {
					
					// for new month
			if (j > last) {
				break;
			}

			registerColors(j, event, nmOfClass)
			document.getElementById('dt-'+j).classList.add(nmOfClass);
		}

		if (classes.indexOf(nmOfClass) == -1) {
			ih += '.'+nmOfClass+' {background: '+eventColors[classes.length]+'}';
			classes.push(nmOfClass);
		}

	}

	style.innerHTML = ih;
			
	document.getElementsByTagName('head')[0].appendChild(style);
	//document.getElementById('someElementId').className = 'cssClass';

	sepEvents()
}

// search for friends
var chosenFriends = [];
var lastVal = '';
function searchForFriend (e=null) {

	if (e != null) {var val = e;} else {var val = lastVal}

	var res = '';
	for (var i = 0; i < chosenFriends.length; i++) {
		res += '<button onclick="addFriend(event, -1)" class="resultFriendsListCard chosenFriend">' + chosenFriends[i] + '</button>'
	}

	if (!val) {
		document.getElementById('resultFriendsList').innerHTML = res;
		return;
	}

	lastVal = val;

	for (var i = 0; i < friends.length; i++) {
		if (friends[i].slice(0,val.length) == val) {
			if (chosenFriends.indexOf(friends[i]) == -1) {
				res += '<button onclick="addFriend(event, 1)" class="resultFriendsListCard">' + friends[i] + '</button>';
			}
		}
	}
			
	res += '<button class="resultFriendsListCard directValue">' + val + '</button>';
	//res += '<button class="resultFriendsListCard directValue"><l class="material-icons">link</i>' + val + '</button>';
	document.getElementById('resultFriendsList').innerHTML = res;
}

function addFriend (e, state) {
			
	ele = e.target;
	if (state == 1) {
		chosenFriends.push(ele.innerHTML);
	} else if (state == -1) {
		chosenFriends.splice(chosenFriends.indexOf(ele.innerHTML),1)
	}
	document.getElementById('friendInvite').value = '';
	searchForFriend('');
}

var lastDay = 0;
function openInfoModal (dayNr) {
	lastDay = dayNr;
	colorPickerLock = true;
	set = null;
	eraseColor()
	$("#infoModal").modal('show');

	eventsDay = days[dayNr]

	var r = '';
			
	for (var i = 0; i < eventsDay.length; i++) {
		event = eventsDay[i][0];
				
		let func = "changeSectionInModal(" + event.id + ")"

		r += '<article onclick="'+func+'" class="eventFeedCardWrapper '+event.class+'">';
		r += '<div class="eventFeedCardInner">'
		r += '<h4 style="width:60%">' + event.name + '</h5>';
		r += '<h6><i class="material-icons" style="vertical-align: middle;">group</i> ' + event.ptp.slice(0,event.ptp.length-1).replaceAll('-', ', ') + '</h6>';
		r += '<p>' + event.desc + '</p>'
		r += '<p><strong>' + 'Sted: ' + '</strong>' + event.place + '</p>';
		r += '<p class="eventCardStart">' + event.start + '</p>'
		r += '<p class="eventCardEnd">' + event.end + '</p>'
		r += '</div></article>';
	}
	$('#eventFeed').html(r)
}

function getEventById(id) {
	for (var i = 0; i < events.length; i++) {if (events[i].id == id) {return events[i];}}
	return -1;
}

function goBack() {
	document.getElementById('eventFeed').style.display = 'block';
	document.getElementById('updateEvent').style.display = 'none';
}

function deleteEvent (id) {

	url = "manage?type=delete&hk="+scKode+"&user="+user+"&eveID="+id;

	$.ajax({url: url, success: function(result){
		console.log(result)
		if (result == '[SUCCESS]') {
			window.location.reload();
		}
	}});
}

function backOut(id) {

	url = "manage?type=removeuser&hk="+scKode+"&user="+user+"&eveID="+id;

	$.ajax({url: url, success: function(result){
		console.log(result)
		if (result == '[SUCCESS]') {
			window.location.reload();
		}
	}});
}


function changeSectionInModal (id) {
	document.getElementById('eventFeed').style.display = 'none';
	var wrapper = document.getElementById('updateEvent');
	wrapper.style.display = 'block';

	var e = getEventById(id);
	var r = '';

	r += '<article class="eventCardWrapper '+e.class+'">';
	r += '<div class="eventFeedCardInner">';
			
	r += '<h4 style="width:60%">' + e.name + '</h5>';
	r += '<p>' + e.desc + '</p>'
	r += '<p><i class="material-icons" style="vertical-align: middle;">group</i><strong> ' + e.ptp.slice(0,e.ptp.length-1).replaceAll('-', ', ') + '</strong></p>';

	r += '<button onclick="deleteEvent('+ e.uidf +')" class="btn btn-outline-danger">Slet aftale</button>&nbsp;'
			
	//NEEDS RETOUCH
	if (e.ptp.length > 0) {
		r += '<button onclick="backOut('+ e.uidf +')" class="btn btn-outline-dark">Meld fra</button>'
	}

	r += '</div></article>';
	r += '<i onclick="goBack()" id="goBackArrowChange" class="material-icons">keyboard_backspace</i>';

	wrapper.innerHTML = r;
}