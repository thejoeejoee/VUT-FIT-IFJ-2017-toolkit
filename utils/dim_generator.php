<?php

function generateRandomString($length = 10) {
    $characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $charactersLength = strlen($characters);
    $randomString = '';
    for ($i = 0; $i < $length; $i++) {
        $randomString .= $characters[rand(0, $charactersLength - 1)];
    }
    return $randomString;
}

$one_of_strings = "";

echo "scope \n";
for($i = 0 ; $i < 1000; $i++) {
    $generate_string = generateRandomString(30);
    if($i == 0)
        $one_of_string = $generate_string;
    echo "dim ".$generate_string." as integer = ".$i."\n";
    
    if(rand(1, 50) == 20)
        $one_of_string = $generate_string;
}
echo "print ".$one_of_string.";\n";
echo "end scope \n";