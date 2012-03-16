<?php

require_once("config.php");

class OracleInterface {
  protected $use_transaction=False;
  protected $username;
  protected $password;
  protected $db_alias;
  protected $connection=NULL;
 

  public function init() {
    if(!$this->connection) {
      putenv("ORACLE_HOME=" . ORACLE_HOME);
      $this->connection = @oci_connect($this->username, $this->password, $this->db_alias);
      if(!$this->connection) {
        throw new DataServerException("{$this->db_alias} connection failed");
      }

      if($this->use_transaction) {
        $statement = oci_parse($this->connection, "SET TRANSACTION READ ONLY");
        oci_execute($statement);
        oci_free_statement($statement);
      }
    }
  }

  public function close() {
    $statement = oci_parse($this->connection, "COMMIT");
    if($this->use_transaction) {
      oci_execute($statement);
      oci_free_statement($statement);
      oci_close($this->connection);
    }
  }

  protected function getArrayResult($sql) {
    $statement = oci_parse($this->connection, $sql);
    oci_execute($statement);

    $output = array();
    while($next_row = oci_fetch_assoc($statement)) {
      $output[] = $next_row;
    }

    oci_free_statement($statement);
    return $output;
  }

  protected function getSingleResult($sql) {
    $statement = oci_parse($this->connection, $sql);
    oci_execute($statement);

    if($result = oci_fetch_assoc($statement)) {
      oci_free_statement($statement);
      return $result;
    } else {
      oci_free_statement($statement);
      return NULL;
    }
  }
}



class TechCash extends OracleInterface {
  protected $use_transaction=True;
  protected $username=TECHCASH_ORACLE_USER;
  protected $password=TECHCASH_ORACLE_PASS;
  protected $db_alias=TECHCASH_ORACLE_DB;

  public function getAccountNumbers($mit_id) {
    $sql = "SELECT DISTINCT ACCOUNTNUMBER, ACCOUNTTYPE " . self::from_where_clause($mit_id);
    return $this->getArrayResult($sql);
  }
       
  public function getLatestBalance($mit_id, $account_id) {
    // uses the POSTDATE to have the most accurate version of current balance
    $sql = "SELECT * FROM (SELECT CURRENTPRIMARYKEY, POSTDATE, BALVALUEAFTERTRAN, ACCOUNTNUMBER " . 
         self::from_where_clause($mit_id, $account_id) .
         " ORDER BY POSTDATE DESC) WHERE ROWNUM < 2";

    return $this->getArrayResult($sql);
    /*
    $row = $this->getSingleResult($sql);
    if(count($row) == 1) {
      return $row['BALVALUEAFTERTRAN'];
    } else {
      return 0;
    }
    */
  }
    
  public function getTransactionsSince($mit_id, $account_id, $limit) {
    $tran_date_field = "MAX(TO_CHAR(TRANDATE,'MM/DD/YYYYHH24:MI:SS'))";

    $limit += 1;

    $sql = "SELECT * FROM (SELECT {$tran_date_field}, MAX(LONGDES), SUM(APPRVALUEOFTRAN), MAX(BALVALUEAFTERTRAN) " . 
           self::from_where_time_clause($mit_id, $account_id) .
           " GROUP BY TRANSID ORDER BY MAX(TRANDATE) DESC) WHERE ROWNUM < {$limit}";

    $rows = $this->getArrayResult($sql);
    $results = array();

    foreach($rows as $index => $row) {
      $results[] = array( 
	 "UNIX_TRANDATE" => strtotime($row[$tran_date_field]),
         "APPRVALUEOFTRAN" => -1 * $row['SUM(APPRVALUEOFTRAN)'],
         "LOCATION" =>  $row["MAX(LONGDES)"]
      );
    }

    return $results;
  }

  public function getAllTransactions($mit_ids, $account_id, $limit) {
    $tran_date_field = "MAX(TO_CHAR(TRANDATE,'MM/DD/YYYYHH24:MI:SS'))";

    $limit += 1;

    $sql = "SELECT * FROM (SELECT TRANSID, MAX(CURRENTPRIMARYKEY), {$tran_date_field}, MAX(LONGDES), SUM(APPRVALUEOFTRAN), MAX(BALVALUEAFTERTRAN) " . 
           self::from_all_time_clause($mit_ids, $account_id) .
           " GROUP BY TRANSID ORDER BY MAX(TRANDATE)) WHERE ROWNUM < {$limit}";

    $rows = $this->getArrayResult($sql);
    $results = array();

    foreach($rows as $index => $row) {
      $results[] = array( 
	 "TRANSID" => $row["TRANSID"],
	 "CURRENTPRIMARYKEY" => $row["MAX(CURRENTPRIMARYKEY)"],
	 "UNIX_TRANDATE" => strtotime($row[$tran_date_field]),
         "APPRVALUEOFTRAN" => $row['SUM(APPRVALUEOFTRAN)'],
         "LOCATION" =>  $row["MAX(LONGDES)"],
         "BALVALUEAFTERTRAN" => $row["MAX(BALVALUEAFTERTRAN)"]
      );
    }

    return $results;
  }

  public function getAllTransactionsForOne($mit_id, $account_id, $limit) {
    $tran_date_field = "MAX(TO_CHAR(TRANDATE,'MM/DD/YYYYHH24:MI:SS'))";

    $limit += 1;

    $sql = "SELECT * FROM (SELECT TRANSID, MAX(CURRENTPRIMARYKEY), {$tran_date_field}, MAX(LONGDES), SUM(APPRVALUEOFTRAN), MAX(BALVALUEAFTERTRAN) " . 
           self::from_past_clause($mit_id, $account_id) .
           " GROUP BY TRANSID ORDER BY MAX(TRANDATE)) WHERE ROWNUM < {$limit}";

    $rows = $this->getArrayResult($sql);
    $results = array();

    foreach($rows as $index => $row) {
      $results[] = array( 
	 "TRANSID" => $row["TRANSID"],
	 "CURRENTPRIMARYKEY" => $row["MAX(CURRENTPRIMARYKEY)"],
	 "UNIX_TRANDATE" => strtotime($row[$tran_date_field]),
         "APPRVALUEOFTRAN" => $row['SUM(APPRVALUEOFTRAN)'],
         "LOCATION" =>  $row["MAX(LONGDES)"],
         "BALVALUEAFTERTRAN" => $row["MAX(BALVALUEAFTERTRAN)"]
      );
    }

    return $results;
  }


  public function getAllTransactionsSince($mit_ids, $account_id, $limit) {
    $tran_date_field = "MAX(TO_CHAR(TRANDATE,'MM/DD/YYYYHH24:MI:SS'))";

    $limit += 1;

    $sql = "SELECT * FROM (SELECT TRANSID, MAX(CURRENTPRIMARYKEY), {$tran_date_field}, MAX(LONGDES), SUM(APPRVALUEOFTRAN), MAX(BALVALUEAFTERTRAN) " . 
           self::from_recent_time_clause($mit_ids, $account_id) .
           " GROUP BY TRANSID ORDER BY MAX(TRANDATE)) WHERE ROWNUM < {$limit}";

    $rows = $this->getArrayResult($sql);
    $results = array();

    foreach($rows as $index => $row) {
      $results[] = array( 
	 "TRANSID" => $row["TRANSID"],
	 "CURRENTPRIMARYKEY" => $row["MAX(CURRENTPRIMARYKEY)"],
	 "UNIX_TRANDATE" => strtotime($row[$tran_date_field]),
         "APPRVALUEOFTRAN" => $row['SUM(APPRVALUEOFTRAN)'],
         "LOCATION" =>  $row["MAX(LONGDES)"],
         "BALVALUEAFTERTRAN" => $row["MAX(BALVALUEAFTERTRAN)"]
      );
    }

    return $results;
  }

  public function getLatestTransactions($mit_id, $account_id, $limit) {
    $tran_date_field = "MAX(TO_CHAR(TRANDATE,'MM/DD/YYYYHH24:MI:SS'))";

    $limit += 1;

    $sql = "SELECT * FROM (SELECT {$tran_date_field}, MAX(LONGDES), SUM(APPRVALUEOFTRAN), MAX(BALVALUEAFTERTRAN) " . 
           self::from_where_clause($mit_id, $account_id) .
           " GROUP BY TRANSID ORDER BY MAX(TRANDATE) DESC) WHERE ROWNUM < {$limit}";

    $rows = $this->getArrayResult($sql);
    $results = array();

    foreach($rows as $index => $row) {
      $results[] = array( 
	 "UNIX_TRANDATE" => strtotime($row[$tran_date_field]),
         "APPRVALUEOFTRAN" => -1 * $row['SUM(APPRVALUEOFTRAN)'],
         "LOCATION" =>  $row["MAX(LONGDES)"]
      );
    }

    return $results;
  }

  public function getMitID($username) {
    $kerberos = strtoupper($username);
    $sql = "SELECT MITID FROM LOCAL_KERBEROS_V WHERE KERBEROS='$kerberos'";
    return $this->getSingleResult($sql);
  }

  private static function compare_by_date($a, $b) {
    $time_a = $a['UNIX_TRANDATE'];
    $time_b = $b['UNIX_TRANDATE'];

    if ($time_a == $time_b) {
      return 0;
    }
    return ($time_a < $time_b) ? 1 : -1;
  }

  private static function from_where_clause($mit_id, $account_id=NULL) {
    $clause =  "FROM Diebold.Web_GeneralLedger_V WHERE TRANSTATUS = 'C' AND CURRENTPRIMARYKEY ='{$mit_id}'";
    if($account_id) {
      $clause .= " AND ACCOUNTNUMBER='{$account_id}'";
    }
    return $clause;
  }

  private static function from_where_time_clause($mit_id, $account_id=NULL) {
    $clause =  "FROM Diebold.Web_GeneralLedger_V WHERE TRANSTATUS = 'C' AND CURRENTPRIMARYKEY ='{$mit_id}' AND TRANDATE > (SYSDATE-10)";
    //$clause =  "FROM Diebold.Web_GeneralLedger_V WHERE TRANSTATUS = 'C' AND TRANDATE > (SYSDATE-1)";
    if($account_id) {
      $clause .= " AND ACCOUNTNUMBER='{$account_id}'";
    }
    return $clause;
  }

  private static function from_past_clause($mit_id, $account_id=NULL) {
    // for getting data for one mit id, contrast to from_all_time_clause 
    $clause =  "FROM Diebold.Web_GeneralLedger_V WHERE TRANSTATUS = 'C' AND CURRENTPRIMARYKEY = '{$mit_id}' AND TRANDATE > (SYSDATE-365)";
    if($account_id) {
      $clause .= " AND ACCOUNTNUMBER='{$account_id}'";
    }
    return $clause;
  }

  private static function from_all_time_clause($mit_ids, $account_id=NULL) {
    // for getting data for several mit ids
    $mit_ids_clause = 'AND (';
    foreach ($mit_ids as $index => $mit_id) {
	if ($index == 0) {
	  $mit_ids_clause .= "CURRENTPRIMARYKEY='{$mit_id}'";
	}
	else {
	  $mit_ids_clause .= "OR CURRENTPRIMARYKEY='{$mit_id}'";
	}
    }
    $mit_ids_clause .= ')';
    $clause =  "FROM Diebold.Web_GeneralLedger_V WHERE TRANSTATUS = 'C' {$mit_ids_clause} AND TRANDATE > (SYSDATE-365)";
    if($account_id) {
      $clause .= " AND ACCOUNTNUMBER='{$account_id}'";
    }
    return $clause;
  }

  private static function from_recent_time_clause($mit_ids, $account_id=NULL) {
    $mit_ids_clause = 'AND (';
    foreach ($mit_ids as $index => $mit_id) {
	if ($index == 0) {
	  $mit_ids_clause .= "CURRENTPRIMARYKEY='{$mit_id}'";
	}
	else {
	  $mit_ids_clause .= "OR CURRENTPRIMARYKEY='{$mit_id}'";
	}
    }
    $mit_ids_clause .= ')';
    $clause =  "FROM Diebold.Web_GeneralLedger_V WHERE TRANSTATUS = 'C' {$mit_ids_clause} AND TRANDATE > (SYSDATE-1)";
    if($account_id) {
      $clause .= " AND ACCOUNTNUMBER='{$account_id}'";
    }
    return $clause;
  }


  public function getOTNTransactionsAll($account_id, $limit) {
    // Get OTN transactions for past year with certain number of $limit
 
    $tran_date_field = "MAX(TO_CHAR(T.TRANDATE,'MM/DD/YYYYHH24:MI:SS'))";

    $limit += 1;

    $sql = "SELECT * FROM (SELECT T.TRANSID, MAX(T.CURRENTPRIMARYKEY), {$tran_date_field}, MAX(T.LONGDES), SUM(T.APPRVALUEOFTRAN), MAX(T.BALVALUEAFTERTRAN) " . 
           self::from_otn_clause($account_id) .
           " GROUP BY T.TRANSID ORDER BY MAX(T.TRANDATE)) WHERE ROWNUM < {$limit}";

    $rows = $this->getArrayResult($sql);
    $results = array();

    foreach($rows as $index => $row) {
      $results[] = array( 
	 "TRANSID" => $row["TRANSID"],
	 "CURRENTPRIMARYKEY" => $row["MAX(T.CURRENTPRIMARYKEY)"],
	 "UNIX_TRANDATE" => strtotime($row[$tran_date_field]),
         "APPRVALUEOFTRAN" => $row['SUM(T.APPRVALUEOFTRAN)'],
         "LOCATION" =>  $row["MAX(T.LONGDES)"],
         "BALVALUEAFTERTRAN" => $row["MAX(T.BALVALUEAFTERTRAN)"]
      );
    }

    return $results;
  }

	//select from generalledger PatronID PatronID from Diebold.Web_PatronInfo_V where HOUSINGCODE='OTN';
  private static function from_otn_clause($account_id=NULL) {
    $clause =  "FROM (SELECT * FROM Diebold.Web_PatronInfo_V WHERE HOUSINGCODE = 'OTN') OTN, Diebold.Web_GeneralLedger_V T WHERE T.TRANSTATUS = 'C' AND T.PATRONID=OTN.PATRONID AND T.TRANDATE > (SYSDATE-365)";
    if($account_id) {
      $clause .= " AND T.ACCOUNTNUMBER='{$account_id}'";
    }
    return $clause;
  }

  public function getOTNTransactionsSince($account_id, $limit) {
    // Get OTN transactions for past day with certain number of $limit
 
    $tran_date_field = "MAX(TO_CHAR(T.TRANDATE,'MM/DD/YYYYHH24:MI:SS'))";

    $limit += 1;

    $sql = "SELECT * FROM (SELECT T.TRANSID, MAX(T.CURRENTPRIMARYKEY), {$tran_date_field}, MAX(T.LONGDES), SUM(T.APPRVALUEOFTRAN), MAX(T.BALVALUEAFTERTRAN) " . 
           self::from_otn_recent_clause($account_id) .
           " GROUP BY T.TRANSID ORDER BY MAX(T.TRANDATE) DESC) WHERE ROWNUM < {$limit}";

    $rows = $this->getArrayResult($sql);
    $results = array();

    foreach($rows as $index => $row) {
      $results[] = array( 
	 "TRANSID" => $row["TRANSID"],
	 "CURRENTPRIMARYKEY" => $row["MAX(T.CURRENTPRIMARYKEY)"],
	 "UNIX_TRANDATE" => strtotime($row[$tran_date_field]),
         "APPRVALUEOFTRAN" => $row['SUM(T.APPRVALUEOFTRAN)'],
         "LOCATION" =>  $row["MAX(T.LONGDES)"],
         "BALVALUEAFTERTRAN" => $row["MAX(T.BALVALUEAFTERTRAN)"]
      );
    }

    return $results;
  }

  private static function from_otn_recent_clause($account_id=NULL) {
    $clause =  "FROM (SELECT * FROM Diebold.Web_PatronInfo_V WHERE HOUSINGCODE = 'OTN') OTN, Diebold.Web_GeneralLedger_V T WHERE T.TRANSTATUS = 'C' AND T.PATRONID=OTN.PATRONID AND T.TRANDATE > (SYSDATE-1/24)";
    if($account_id) {
      $clause .= " AND T.ACCOUNTNUMBER='{$account_id}'";
    }
    return $clause;
  }

  public function getOTNLatestBalances($account_id) {
    // uses the POSTDATE to have the most accurate version of current balance
    $sql = "SELECT * FROM (SELECT T.CURRENTPRIMARYKEY, T.POSTDATE, T.BALVALUEAFTERTRAN, T.ACCOUNTNUMBER, ROW_NUMBER() OVER (PARTITION BY T.CURRENTPRIMARYKEY ORDER BY T.POSTDATE DESC) RN " .
	self::from_otn_where_clause($account_id) .
	" ORDER BY T.CURRENTPRIMARYKEY) WHERE RN=1";

    return $this->getArrayResult($sql);
  }
 
  private static function from_otn_where_clause($account_id=NULL) {
    // used by getOTNLatestBalances
    $clause =  "FROM (SELECT * FROM Diebold.Web_PatronInfo_V WHERE HOUSINGCODE = 'OTN') OTN, Diebold.Web_GeneralLedger_V T WHERE T.TRANSTATUS = 'C' AND T.PATRONID=OTN.PATRONID";
    if($account_id) {
      $clause .= " AND T.ACCOUNTNUMBER='{$account_id}'";
    }
    return $clause;
  }



  // For Testing and understanding the DB
  public function getOTN_MITs() {
    // get OTN MIT id's
    $sql = "SELECT DISTINCT T.CURRENTPRIMARYKEY, T.PATRONID FROM (SELECT * FROM Diebold.Web_PatronInfo_V WHERE HOUSINGCODE = 'OTN') OTN, Diebold.Web_GeneralLedger_V T WHERE OTN.PATRONID=T.PATRONID";
    return $this->getArrayResult($sql);
  }

  // OTN Patrons
  public function getPatronInfoFields() {
    $sql = "SELECT * FROM Diebold.Web_PatronInfo_V WHERE HOUSINGCODE = 'OTN'";
    return $this->getArrayResult($sql);
  }

  public function getAccountInfo($mit_id) {
    $sql = "SELECT * " . self::from_where_clause($mit_id);
    return $this->getArrayResult($sql);
  }
 
  public function getOTNTest( $account_id=NULL, $limit ) {
    $tran_date_field = "MAX(TO_CHAR(TRANDATE,'MM/DD/YYYYHH24:MI:SS'))";

    $sql = "SELECT * FROM (SELECT T.TRANSID, MAX(T.CURRENTPRIMARYKEY), {$tran_date_field}, MAX(T.LONGDES), SUM(T.APPRVALUEOFTRAN), MAX(T.BALVALUEAFTERTRAN) " . 
           self::from_otn_clause($account_id) .
           " GROUP BY T.TRANSID ORDER BY MAX(T.TRANDATE)) WHERE ROWNUM < {$limit}";
    return $this->getArrayResult($sql);
  }

  //  Testing END

  public static function dollar_string($cents) {
    $sign = ($cents < 0) ? '-' : '';
    $cents = abs($cents); 

    $dollars = floor($cents / 100);
    $cents = $cents % 100;
    if($cents < 10) {
      $cents = '0' . $cents;
    }
    return "$sign$dollars.$cents";
  }

  public static function dollar_string_rows($rows, $fields) {
    foreach($rows as $index => $row) {
      foreach($fields as $field) {
        $rows[$index][$field] = self::dollar_string($rows[$index][$field]);
      }
    }
    return $rows;
  }

  public function getAccountName($account_type) {
    $sql = "SELECT DESCRIPTION FROM WEB_SVCPLANINFO_V WHERE PLANID={$account_type}";
    $row = $this->getSingleResult($sql);
    return $row["DESCRIPTION"];
  }

}


  

class Warehouse extends OracleInterface {
  protected $username=TECHCASH_WAREHOUSE_USER;
  protected $password=TECHCASH_WAREHOUSE_PASS;
  protected $db_alias=TECHCASH_WAREHOUSE_DB;

  public function getMitID($name) {
    $sql = "SELECT MIT_ID FROM KRB_MAPPING WHERE KRB_NAME='$name'";
    return $this->getSingleResult($sql);
  }
}

function getMitID($techcash, $username) {
  $row = $techcash->getMitID($username);
  if($row) {
    return $row['MITID'];
  } 

  $warehouse = new Warehouse();
  $warehouse->init();
  $row = $warehouse->getMitID($username);
  $warehouse->close(); 

  if($row) {
    return $row['MIT_ID'];
  }
}

?>
