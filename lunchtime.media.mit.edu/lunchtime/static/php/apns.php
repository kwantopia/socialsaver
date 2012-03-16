<?php

// msg_type: lunch, receipt


$production=true;
//$deviceToken = '02da851dXXXXXXXXb4f2b5bfXXXXXXXXce198270XXXXXXXX0d3dac72bc87cd60'; // masked for security reason

// kwan's iphone
$deviceToken = 'bd868ce1ba22bb1ed1015bcebe6b63c18568e1f6ca4e0c0dc5f0f1e8ee99443d';
// erik's device possibly
// $deviceToken = '4bae594f6f757b53376b94e8939b471f7ecd3f96e892dae215de3d6693984553';
// John McDonald's
#$deviceToken = 'a48ad9fd387a1410d2a99e1b5da64cae52664ad024028ffb121bbb1aa84f7a14';
// yod's iphone
#$deviceToken = 'fc8041eff072292345d1985a510adfc61f6090e372e5223c6ee456f042b74573';
// Passphrase for the private key (ck.pem file)
//$pass = '1nndura';
// Get the parameters from http get or from command line
$message = $_GET['message'] or $message = $argv[1] or $message = 'Message received from javacom';
$badge = (int)$_GET['badge'] or $badge = (int)$argv[2];
$sound = $_GET['sound'] or $sound = $argv[3];
// Construct the notification payload
$body = array();
$body['aps'] = array('alert' => $message);
if ($badge)
$body['aps']['badge'] = $badge;
if ($sound)
$body['aps']['sound'] = $sound;
$body['msg_type'] = 'lunch';
/* End of Configurable Items */
$ctx = stream_context_create();
if ($production) {
    // Production
    stream_context_set_option($ctx, 'ssl', 'local_cert', '../../keys/iphone_live.pem');
    // assume the private key passphase was removed.
    //stream_context_set_option($ctx, 'ssl', 'passphrase', $pass);
    // Production
    $fp = stream_socket_client('ssl://gateway.push.apple.com:2195', $err, $errstr, 60, STREAM_CLIENT_CONNECT, $ctx);
} else {
    // Sandbox
    stream_context_set_option($ctx, 'ssl', 'local_cert', '../../keys/iphone_ck.pem');
    //stream_context_set_option($ctx, 'ssl', 'passphrase', $pass);
    // Sandbox
    $fp = stream_socket_client('ssl://gateway.sandbox.push.apple.com:2195', $err, $errstr, 60, STREAM_CLIENT_CONNECT, $ctx);
}
if (!$fp) {
print "Failed to connect $err $errstrn";
return;
}
else {
print "Connection OK\n";
}
$payload = json_encode($body);
$msg = chr(0) . pack("n",32) . pack('H*', str_replace(' ', '', $deviceToken)) . pack("n",strlen($payload)) . $payload;
print "sending message :" . $payload . "\n";
fwrite($fp, $msg);
fclose($fp);
?>
