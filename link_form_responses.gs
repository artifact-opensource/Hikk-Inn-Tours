/** Run once in https://script.google.com after replacing the two IDs. */
function linkFormResponses() {
  const FORM_ID = '1nyZthFM8yG7NNEtvs52iLqgEfZntzxYp2JGur-b9cbQ';
  const SPREADSHEET_ID = '1sVPVvLh9ENTGpO-oUxHdke4x0eMAvnvKk2fa-YvhqsE';
  const form = FormApp.openById(FORM_ID);
  form.setDestination(FormApp.DestinationType.SPREADSHEET, SPREADSHEET_ID);
  Logger.log('Linked form responses successfully.');
}
