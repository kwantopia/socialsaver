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

  // account_id is not used anymore
  //		1: TechCASH
  //		2: Employee Payroll Deduction
  

  // the following two lines needed for login
  $fullname = get_fullname();
  $username = get_username();

  $account_id = $_REQUEST['id'];

  $techcash = new TechCash();
  $techcash->init();

  $account_id=NULL;
  $transactions = $techcash->getOTNTransactionsSince($account_id, 100);
  $balances = $techcash->getOTNLatestBalances($account_id);

  $techcash->close();

  $transactions = TechCash::dollar_string_rows($transactions, array("APPRVALUEOFTRAN", "BALVALUEAFTERTRAN"));
  $balances = TechCash::dollar_string_rows($balances, array("BALVALUEAFTERTRAN"));

  $output = array(
		"balances" => $balances,
		"transactions" => $transactions,
		);
  echo json_encode($output);

?>
