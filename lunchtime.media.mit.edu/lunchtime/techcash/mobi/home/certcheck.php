<?php

require_once "../page_builder/page_header.php";

if(!isset($_REQUEST['ref'])) {
  $destination = "/home/";
} else {
  $destination = $_REQUEST['ref'];
}

if(!isset($_REQUEST['name'])) {
  $destination_name = "MIT Mobile Web";
} else {
  $destination_name = $_REQUEST['name'];
}

if(!isset($_REQUEST['image'])) {
  $destination_image = "about";
} else {
  $destination_image = $_REQUEST['image'];
}

require "$page->branch/certcheck.html";
$page->output();

?>
