<?
require "../page_builder/security.php";
require "tech_cash.php";

ssl_required();

  // 02/23/10 - this file was used to test OTN integration of techcash and many
  // 		method calls were tested
  //		getPatronInfoFields() returns OTN patrons information
  //		getOTN_MITs() returns MIT ID's with OTN enabled
  //		getOTNLatestBalances() returns latest balances
  //		getOTNTransactionsAll() returns all OTN user's transactions
  //		getOTNTransactionsSince() returns just last day's transactions

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
  //$mit_ids = $techcash->getOTNMitIds();
  $patrons = $techcash->getPatronInfoFields();
  $mit_ids = $techcash->getOTN_MITs();
  $transactions = $techcash->getOTNTransactionsSince($account_id, 100);
  //$transactions = $techcash->getOTNTest($account_id, 100);
  //$balances = array();
  //foreach ($mit_ids as $mit_id) {
  //	$current_cents =$techcash->getLatestBalance($mit_id, $account_id);
  //  	$current_balance = TechCash::dollar_string($current_cents);
  //	$balances[$mit_id] = $current_balance;
  //}
  $balances = $techcash->getOTNLatestBalances($account_id);
  $techcash->close();

  $transactions = TechCash::dollar_string_rows($transactions, array("APPRVALUEOFTRAN", "BALVALUEAFTERTRAN"));
  $balances = TechCash::dollar_string_rows($balances, array("BALVALUEAFTERTRAN"));

  //$previous_date = $transactions[count($transactions)-1]['UNIX_TRANDATE'];

  $output = array(
		"accountname" => $account_name,
		"balances" => $balances,
		"transactions" => $transactions,
		"patrons" => $patrons,
		"mit" => $mit_ids
		);
  echo json_encode($output);

?>
