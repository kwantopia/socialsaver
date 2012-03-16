<?

/*
 * use this file to store all sensitive info (passwords etc) in one place
 *
 * please put non-sensitive information in constants.php
 * as much as possible, so that if people need to change things we don't
 * have to touch this file
 */

// database parameters
define("MYSQL_USER", 'mobile');
define("MYSQL_PASS", 'mobile');
define("MYSQL_DBNAME", 'mobile');
define("MYSQL_HOST", 'localhost');

/* TECHCASH
 * the techcash file in lib contains information about the structure of 
 * databases in techcash and mit data warehouse.
 * it may or may not be sensitive but if it is, we should remove the 
 * techcash module and all related references (including this section
 * of this file) if/when we pack up our code for open source.
 */
define("ORACLE_HOME", '/oracle/product/10.2.0/client');
define("TECHCASH_ORACLE_USER", 'MITMOB');
define("TECHCASH_ORACLE_PASS", 'mobimobi648');
define("TECHCASH_ORACLE_DB", 'ORACLEGOLD');
define("WAREHOUSE_ORACLE_USER", 'mitmob');
define("WAREHOUSE_ORACLE_PASS", 'mobi648');
define("WAREHOUSE_ORACLE_DB", 'warehouse');

// DRUPAL
define("DRUPAL_MYSQL_USER", 'drupal');
define("DRUPAL_MYSQL_PASS", 'drupal');
define("DRUPAL_MYSQL_DBNAME", 'drupal');
define("DRUPAL_MYSQL_HOST", 'localhost');

?>
