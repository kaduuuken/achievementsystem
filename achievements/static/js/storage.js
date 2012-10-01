var storage = new function () {
	/* --------- Private Properties --------- */

	var dataContainer = {};

	/* --------- Private Methods --------- */

	function linearize () {
		var string = "", name, value;
		for (name in dataContainer) {
			name = encodeURIComponent(name);
			value = encodeURIComponent(dataContainer[name]);
			string += name + "=" + value + "&";
		}
		if (string != "") {
			string = string.substring(0, string.length - 1);
		}
		return string;
	}

	function read () {
		if (window.name == '' || window.name.indexOf("=") == -1) {
			return;
		}
		var pairs = window.name.split("&");
		var pair, name, value;
		for (var i = 0; i < pairs.length; i++) {
			if (pairs[i] == "") {
				continue;
			}
			pair = pairs[i].split("=");
			name = decodeURIComponent(pair[0]);
			value = decodeURIComponent(pair[1]);
			dataContainer[name] = value;
		}
	}

	function write () {
		window.name = linearize();
	}

	/* --------- Public Methods --------- */

	this.set = function (name, value) {
		dataContainer[name] = value;
		write();
	};

	this.get = function (name) {
		var returnValue = dataContainer[name];
		return returnValue;
	};

	this.getAll = function () {
		return dataContainer;
	};

	this.remove = function (name) {
		if (typeof(dataContainer[name]) != undefined) {
			delete dataContainer[name];
		}
		write();
	};

	this.removeAll = function () {
		dataContainer = {};
		write();
	};

	/* --------- Construction --------- */

	read();
};
