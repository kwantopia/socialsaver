<?
require "../page_builder/security.php";
require "../page_builder/page_header.php";
require "tech_cash.php";

ssl_required();
if(!$page->certs) {
  $error_text = 'The mobile browser that you are using does not support MIT personal certicates. At this time only the iPhone, Windows Mobile Internet Explorer, and BlackBerry browsers support certificates. Please use one of the above browsers or use your computer (<a href="http://techcash.mit.edu">http://techcash.mit.edu</a>) to access yourTechCASH account.';

  $page->error_page('TechCASH', 'techcash', $error_text);
  //require "$page->branch/not_supported.html";

} else {

  $fullname = get_fullname();
  $username = get_username();

  $account_id = $_REQUEST['id'];

  $techcash = new TechCash();
  $techcash->init();
  $account_name = $techcash->getAccountName($account_id);
  $mit_id = getMitID($techcash, $username);
  //$mit_id = "111010083";
  //$mit_id = "921645261";
  //$mit_id = "980988037";
  $mit_ids = array( "921645261", "980988037");
  //$transactions = $techcash->getLatestTransactions($mit_id, $account_id, 500);
  //$transactions = $techcash->getTransactionsSince($mit_id, $account_id, 500);
  $transactions = $techcash->getAllTransactionsSince($mit_ids, $account_id, 500);
  $balances = array();
  foreach ($mit_ids as $mit_id) {
  	$current_cents =$techcash->getLatestBalance($mit_id, $account_id);
  	$current_balance = TechCash::dollar_string($current_cents);
	$balances[$mit_id] = $current_balance;
  }
  $techcash->close();

  $transactions = TechCash::dollar_string_rows($transactions, array("APPRVALUEOFTRAN", "BALVALUEAFTERTRAN"));

  //$previous_date = $transactions[count($transactions)-1]['UNIX_TRANDATE'];

  $output = array(
		"balances" => $balances,
		"transactions" => $transactions
		);
  echo json_encode($output);
}

?>
