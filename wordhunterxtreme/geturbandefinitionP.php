<? require_once 'lib/nusoap.php';
$word = $_GET['word'];

define('KEY', 'bc65e461224c030047116e980e9b2a63');

$soap = new soapclient('http://api.urbandictionary.com/soap');
$result = $soap->call('lookup', array('key' => KEY, 'term' => $word));

if($error = $soap->getError()) {
    print $error;
 } else {
    if(count($result)>2){
    	print_r(str_replace("\n",",",$result[0]['definition']));
    }
  }
?>
