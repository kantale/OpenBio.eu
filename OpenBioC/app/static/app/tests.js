
/*
* Run with window.test.test() 
*/
(function (){
	var ret = {};

	ret.click = function(id) {
		$('#' + id).click()
	};

	ret.insert = function(id, text) {
		$('#' + id).val(text).trigger('input');
	};

	var test_1 = function() {
		ret.click('toolsDataPlusBtn');
	};

	var test_2 = function() {
		ret.insert('leftPanelSearch', 'draft');
	}

	ret.tests = [
		test_1,
		test_2
	];

	var build_chain = function(fns, i) {

		if (i>=fns.length) {
			return;
		}

		setTimeout(function() {
			console.log('Running test:', i+1)
			fns[i]();
			build_chain(fns, i+1);
		}, 1000)
	};

	ret.test = function() {
		build_chain(ret.tests, 0);
	};

	window.test = ret;
	//return ret;
})();


