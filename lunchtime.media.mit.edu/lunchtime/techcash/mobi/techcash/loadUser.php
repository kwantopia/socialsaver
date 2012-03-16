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

  $account_id = NULL;
  $transactions = $techcash->getAllTransactionsForOne($mit_id, $account_id, 5000);
  $balances = $techcash->getLatestBalance($mit_id, $account_id);

  $techcash->close();

  $transactions = TechCash::dollar_string_rows($transactions, array("APPRVALUEOFTRAN", "BALVALUEAFTERTRAN"));
  $balances = TechCash::dollar_string_rows($balances, array("BALVALUEAFTERTRAN"));

  //$previous_date = $transactions[count($transactions)-1]['UNIX_TRANDATE'];

  $output = array(
		"balances" => $balances,
		"transactions" => $transactions
		);
  echo json_encode($output);

?>
