/** Run once in https://script.google.com after replacing the two IDs. */
function linkFormResponses() {
  const FORM_ID = 'PASTE_FORM_ID_HERE';
  const SPREADSHEET_ID = 'PASTE_SPREADSHEET_ID_HERE';
  const form = FormApp.openById(FORM_ID);
  form.setDestination(FormApp.DestinationType.SPREADSHEET, SPREADSHEET_ID);
  Logger.log('Linked form responses successfully.');
}
