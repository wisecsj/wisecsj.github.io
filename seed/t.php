
<?php
function random($length) {
	$hash = '';
	$chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz';
	$max = strlen($chars) - 1;
	PHP_VERSION < '4.2.0' && mt_srand((double)microtime() * 1000000);
	for($i = 0; $i < $length; $i++) {
		$hash .= $chars[mt_rand(0, $max)];
	}
	return $hash;
}
$fp = fopen('c.txt', 'rb');
$fp2 = fopen('d.txt', 'wb');
while(!feof($fp)){
	$b = fgets($fp, 4096);
	if(preg_match("/seed=(\d)+/", $b, $matach)){
		$m = $matach[0];
	}else{
		continue;
	}
	// var_dump(substr($m,7));
	mt_srand(substr($m,7));
	fwrite($fp2, random(10)."\n");
}
fclose($fp);
fclose($fp2);