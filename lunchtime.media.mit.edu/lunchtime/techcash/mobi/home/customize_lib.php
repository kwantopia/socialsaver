<?
require_once "modules.php";
define(EXPIRE_TIME, 160 * 24 * 60 * 60);


function getModuleOrder() {
  return explode(",", $_COOKIE["moduleorder"]);
}

function getActiveModules($device) {
  if(!isset($_COOKIE["activemodules"])) {
    return Modules::default_order($device);
  } elseif($_COOKIE["activemodules"]=="NONE") {
    return array();
  } else {
    return explode(",", $_COOKIE["activemodules"]);
  }
}

function setModuleOrder($modules) {
  setcookie("moduleorder", implode(",", $modules), time() + EXPIRE_TIME);
}

function setActiveModules($modules) {
  if(count($modules) > 0) {
    setcookie("activemodules", implode(",", $modules), time() + EXPIRE_TIME);
  } else {
    setcookie("activemodules", "NONE", time() + EXPIRE_TIME);
  }
}

?>