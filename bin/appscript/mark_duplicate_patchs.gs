function checkDuplicates() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("OSS->Video");
  
  var range = sheet.getRange("A:H");
  var values = range.getValues();
  
  var uniqueRows = [];
  
  
  for (var i = 0; i < values.length; i++) {
    if (i == 0) continue;
    
    if (values[i][2].includes("PATRON STOPPED DUE TO UNEXPECTED")) continue;
    if (values[i][2] === "") continue;
    var package = values[i][0]
    var binary = values[i][1]
    var donor = values[i][3]
    var donee = values[i][4]
    var diff = values[i][7]
    if (diff === "") continue;
    
    var secondLine = diff.split('\n')[1].split('.c')[0];
    var patch_path = secondLine.split(' ')[1]
  
    var rowString = package + binary + donee
    if (uniqueRows.indexOf(rowString) === -1) {
      uniqueRows.push(rowString);
      sheet.getRange(i + 1, 12).setValue(patch_path + '.c')
    } else {
      sheet.getRange(i + 1, 9).setValue("duplicate");
    }

  }
}