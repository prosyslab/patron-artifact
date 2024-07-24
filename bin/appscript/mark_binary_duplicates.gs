function myFunction() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("OSS->Video");
  
  var range = sheet.getRange("A:H");
  var values = range.getValues();
  
  var uniqueRows_pkg = [];
  var uniqueRows_bin = [];
  var uniqueRows_diff = [];
  
  for (var i = 0; i < values.length; i++) {
    if (i == 0) continue;
    if (values[i][2].includes("PATRON STOPPED DUE TO UNEXPECTED")) continue;
    if (values[i][2] === "") continue;
  
    var package = values[i][0]
    var binary = values[i][1]
    var diff = values[i][7]
    if (diff === "") continue;
    var restLines = diff.split('\n').slice(3);
    var joined_line = ""
    for (var k = 0; k < restLines.length; k++) {
      if (restLines[k].includes("#line")) {
        continue;
      }
      const pattern1 = /_cil_tmp\d+/g;
      const pattern2 = /while_break___\d+/g;
      var replacedStrings = restLines[k].replace(pattern1, '_cil_tmp').replace(pattern2, 'while_break')
      joined_line = joined_line + replacedStrings
    }

    if (uniqueRows_diff.indexOf(joined_line) === -1) {
      uniqueRows_pkg.push(package);
      uniqueRows_bin.push(binary);
      uniqueRows_diff.push(joined_line);
    } else {
      var idx = uniqueRows_diff.indexOf(joined_line);
      if (uniqueRows_pkg[idx] === package && uniqueRows_bin != binary)
        sheet.getRange(i + 1, 9).setValue("bin-duplicate");
    }

  }
}
