<?php

class Modules {
/** 
 * This class identifies what modules are available for access)
 * 
 * @static
 * @var array $names Identifies the modules that are available for access.
 */

  private static $names = array(
    "people"          => "People Directory",
    "map"             => "Campus Map",
    "shuttleschedule" => "Shuttle Schedule",
    "calendar"        => "Events Calendar",
    "stellar"         => array("Stellar", "class info"),
    "careers"         => "Student Careers",
    "emergency"       => "Emergency Info",
    "3down"           => array("3DOWN", "service status"),
    "techcash"        => "TechCASH (BETA)",
    "links"           => "Useful Links",
  );
  /**
   * Identifies the special modules are contingent upon phone-specific functionality
   * These modules are to be shown in the extras sections for smart-phone/feature-phones
   * They will be treated like ordinary modules for webkit based phones
   * @var array $extras
   */
 
  private static $extras = array(
    "sms"             => "MIT SMS (BETA)",
    "certificates"    => "MIT Cerfiticates",
    "webmitedu"       => "Full MIT Website",
  );

  private static $new = array();

  private static $required = array();

 /**
   * Identifies the additional urls for specific functionality
   * certificates - MIT's certificate access page
   * webmitedu - MIT's homepage
   * about - The mobile about page
   * preferences - The preferences page 
   * @var array $non_default_urls
   */

  private static $non_default_urls = array(
    "certificates"    => "http://ca.mit.edu/",
    "webmitedu"       => "http://web.mit.edu/",
    "about"           => "../mobile-about/",
    "preferences"     => "customize.php",
  );

  private static $certificate_required = array("techcash");
  private static $iphone_only = array("certificates", "techcash");

  
  public static function new_apps() {
    return self::$new;
  }

  public static function new_apps_count() {
    return count(self::$new);
  }
  
  public static function title($module) {
    $names = self::full_list();
    $name = $names[$module];
    return self::make_title($name, True);
  }

  public static function subtitle($module) {
    $names = self::full_list();
    $name = $names[$module];
    return self::make_title($name, False);
  }

  public static function make_title($title_data, $title_mode=True) {
    if(is_array($title_data)) {
      $index = $title_mode ? 0 : 1;
      return $title_data[$index];
    } else {
      return $title_mode ? $title_data : NULL;
    }
  }

  public static function default_order($device) {
    $order = array();

    foreach(self::full_list($device) as $module => $name) {
      if($device == "ip") {
        $order[] = $module;
      } elseif( !in_array($module, self::$iphone_only) ) {
        $order[] = $module;
      }
    }

    return $order;
  }

  public static function full_list($device=NULL) {
    if($device === NULL || in_array($device, array("ip", "ad"))) {
      return array_merge(self::$names, self::$extras);
    }

    return self::$names;
  }
  
  public static function url($module) {
    if(isset(self::$non_default_urls[$module])) {
      return self::$non_default_urls[$module];
    } else {
      return "../$module/";
    }
  }


  public static function certificate_required($module) {
    return in_array($module, self::$certificate_required);
  }

  public static function required($module) {
    return in_array($module, self::$required);
  }

  public static function add_required($modules, $device) {
    foreach(self::default_order($device) as $module) {
      if(self::required($module) && !in_array($module, $modules)) {
        $modules[] = $module;
      }
    }
    return $modules;
  }

  public static function filterExists($modules, $device) {
    $default_list = self::default_order($device);
    $filtered = array();

    foreach($modules as $module) {
      if(in_array($module, $default_list)) {
	$filtered[] = $module;
      }
    }
    return $filtered;
  }

  private static function newModules($modules, $device) {
    $default_list = self::default_order($device);
    $new = array();    

    // add any modules not already in the list
    foreach($default_list as $module) {
      if(!in_array($module, $modules)) {
        $new[] = $module;
      }
    }
    return $new;
  }

  // update the module list, if the users cookies 
  // are inconsistent with the services module list
  public static function refreshAll($all, $device) {
    $refreshed = self::filterExists($all, $device);
    return self::add_new_items($refreshed, self::newModules($all, $device));
  }

  // update the module list, if the users cookies 
  // are inconsistent with the services module list
  public static function refreshActive($all, $active, $device) {
    $refreshed = self::filterExists($active, $device);
    return self::add_new_items($refreshed, self::newModules($all, $device));
  }


  private static function add_new_items($old, $new) {
    foreach($new as $item) {
      if(!in_array($item, $old)) {
        $old[] = $item;
      }
    }
    return $old;
  }
}

?>
