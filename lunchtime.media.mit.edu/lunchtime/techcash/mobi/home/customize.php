<?php
require_once "../page_builder/page_header.php";
require_once "modules.php";
require_once "customize_lib.php";

if($phone == "ip") {
  $modules = Modules::default_order($phone);
  require "ip/customize.html";
} else {
  $modules = getModuleOrder();
  $activemodules = getActiveModules($phone);

  // Process the various possible actions
  if($_REQUEST['action'] == 'swap') {
    $module_1 = $_REQUEST['module1'];
    $module_2 = $_REQUEST['module2'];
    $position_1 = intval($_REQUEST['position1']);
    $position_2 = intval($_REQUEST['position2']);

    //make sure cookie is consistent with action
    // if so swap them
    if( ($modules[$position_1] == $module_1) && ($modules[$position_2] == $module_2) ) {
      $modules[$position_1] = $module_2;
      $modules[$position_2] = $module_1;
    }
  }

  if($_REQUEST['action'] == 'on') {
    $activemodules[] = $_REQUEST['module'];
  }

  if($_REQUEST['action'] == 'off') {
    $module = $_REQUEST['module'];
    if(in_array($module, $activemodules)) {
      array_splice($activemodules, array_search($module, $activemodules), 1);
    }
  }



  // reorder active modules to be consistent with the module-order
  $old_activemodules = $activemodules;
  $activemodules = array();
  foreach($modules as $module) {
    if(in_array($module, $old_activemodules)) {
      $activemodules[] = $module;
    }
  }
  $activemodules = Modules::add_required($activemodules, $phone);

  $old_modules = $modules;
  $modules = Modules::refreshAll($old_modules, $phone);
  $activemodules = Modules::refreshActive($old_modules, $activemodules, $phone);

  setModuleOrder($modules);
  setActiveModules($activemodules);

  $menu = array();
  foreach($modules as $index => $module) {
    
    $status = in_array($module, $activemodules) ? "on" : "off";

    // required modules can not be toggled on and off
    $toggle_action = NULL;
    if(!Modules::required($module)) {
      $toggle_action = in_array($module, $activemodules) ? "off" : "on";
    }

    $menu[] = array(
      "name" => $module,
      "status" => $status,
      "toggle_action" => $toggle_action,
      "toggle_url" => toggle_url($module, $toggle_action),
      "swap_up_url" => swap_url($module, $index, $modules[$index-1], $index-1),
      "swap_down_url" => swap_url($module, $index, $modules[$index+1], $index+1)
    );
  }

  switch($phone) {
    case "sp":
      $checkbox_size = 16;
      $arrow_width = 15;
      $arrow_height = 16;
      break;

    case "fp":
      $checkbox_size = 12;
      $arrow_width = 11;
      $arrow_height = 12;
      break;

  }

  if($phone == "ad") {
    require "ad/customize.html";
  } else {  
    require "$prefix/customize.html";
  }
}


$page->output();

function toggle_url($module, $action) {
  if($action) {
    return "customize.php?action=$action&module=$module";
  }
}

function swap_url($module1, $position1, $module2, $position2) {

  if($module1 && $module2) {
    return "customize.php?action=swap&module1=$module1&position1=$position1&module2=$module2&position2=$position2";
  }
}

?>