const { exec } = require('child_process');
const GET_PACKAGE_NAME = 'adb shell "dumpsys activity | grep top-activity"';

function removePackage(name){
	const REMOVE_PACKAGE = 'adb shell pm uninstall -k --user 0 ' + name;
	exec(REMOVE_PACKAGE, (err, stdout, stderr) => {
	    if (err) {
	    	console.log(err); return;
	    }
	    console.log('removed! ' + name)
	})
}

function getPackageName(){
	exec(GET_PACKAGE_NAME, (err, stdout, stderr) => {
	    if (err) {
	      // node couldn't execute the command
	      return;
	    }

	    let name = stdout.match(/.*(com.*)\//)[1];

	    removePackage(name);
	})
}

getPackageName();