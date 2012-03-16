<?
require "../page_builder/security.php";
class DataServerException extends Exception {
}
function exception_handler($exception) {

  if(is_a($exception, "DataServerException")) {
    $error_query = "code=data&url=" . urlencode($_SERVER['REQUEST_URI']);
  } else if(is_a($exception, "DeviceNotSupported")) {
    $error_query = "code=device_notsupported";
  } else {
    $error_query = "code=internal";
  }
  $error_url = "../error-page/?{$error_query}";

  // a text representation of the exception
  ob_start();
    var_dump($exception);
  $text = ob_get_contents();
  ob_end_clean();

  if(!Page::is_spider()) {
    mail(
      DEVELOPER_EMAIL, 
      "mobile web page experiencing problems",
      "the following url is throwing exceptions: http://mobi.mit.edu{$_SERVER['REQUEST_URI']}\n" .
      "Exception:\n" . 
      "$text\n" .
      "The User-Agent: \"{$_SERVER['HTTP_USER_AGENT']}\"\n" .
      "The referer URL: \"{$_SERVER['HTTP_REFERER']}\""
    );
  }

  header("Location: {$error_url}");
  die(0);
}
require "tech_cash.php";

  $account_id = 1; 

  $techcash = new TechCash();
  $techcash->init();
  $account_name = $techcash->getAccountName($account_id);
  $mit_id = getMitID($techcash, $username);
  //$mit_id = "111010083";
  $mit_id = "921645261";
  $mit_id = "980988037";
  //$transactions = $techcash->getLatestTransactions($mit_id, $account_id, 500);
  $transactions = $techcash->getTransactionsSince($mit_id, $account_id, 500);
  $current_cents =$techcash->getLatestBalance($mit_id, $account_id);
  $techcash->close();

  $current_balance = TechCash::dollar_string($current_cents);

  $transactions = TechCash::dollar_string_rows($transactions, array("APPRVALUEOFTRAN", "BALVALUEAFTERTRAN"));

  $previous_date = $transactions[count($transactions)-1]['UNIX_TRANDATE'];

  $output = array(
		"mit_id" => $mit_id,
		"current_balance" => $current_balance,
		"previous_date" => $previous_date,
		"count" => count($transactions),
		"transactions" => $transactions
		);
  echo json_encode($output);
?>
