<?
require "../page_builder/security.php";
require "tech_cash.php";

ssl_required();

  $fullname = get_fullname();
  $username = get_username();

  $account_id = $_REQUEST['id'];
  $mit_id = $_REQUEST['mit'];

  $techcash = new TechCash();
  $techcash->init();
  $account_name = $techcash->getAccountName($account_id);
  #$mit_id = getMitID($techcash, $username);
  $mit_ids = array( $mit_id ); 
  //$transactions = $techcash->getLatestTransactions($mit_id, $account_id, 500);
  //$transactions = $techcash->getTransactionsSince($mit_id, $account_id, 500);
  $transactions = $techcash->getAllTransactions($mit_ids, $account_id, 5000);
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

?>
