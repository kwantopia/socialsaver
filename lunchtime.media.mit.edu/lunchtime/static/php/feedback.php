#!/usr/bin/env php
<?php

$ctx = stream_context_create();
stream_context_set_option($ctx, 'ssl', 'local_cert', '../../keys/iphone_live.pem');
stream_context_set_option($ctx, 'ssl', 'verify_peer', false);
// assume the private key passphase was removed.
// stream_context_set_option($ctx, 'ssl', 'passphrase', $pass);


$fp = stream_socket_client('ssl://feedback.push.apple.com:2196', $error, $errorString, 60, STREAM_CLIENT_CONNECT, $ctx);
// production server is ssl://feedback.push.apple.com:2196

if (!$fp) {
    print "Failed to connect feedback server: $err $errstr\n";
    return;
}
else {
   print "Connection to feedback server OK\n";
}

        print "APNS feedback results\n";
        while ($devcon = fread($fp, 38))
        {
   $arr = unpack("H*", $devcon); 
   $rawhex = trim(implode("", $arr));
   $feedbackTime = hexdec(substr($rawhex, 0, 8)); 
   $feedbackDate = date('Y-m-d H:i', $feedbackTime); 
   $feedbackLen = hexdec(substr($rawhex, 8, 4)); 
   $feedbackDeviceToken = substr($rawhex, 12, 64);
   print "TIMESTAMP:" . $feedbackDate . "\n";
          print "DEVICE ID:" . $feedbackDeviceToken. "\n\n";
        }
fclose($fp);
?>