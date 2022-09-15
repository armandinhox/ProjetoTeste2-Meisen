<?php

require_once "./vendor/autoload.php";
use thiagoalessio\TesseractOCR\TesseractOCR;


$random = (float)rand()/(float)getrandmax()*2;
$url = 'http://www.sintegra.fazenda.pr.gov.br/sintegra/captcha?'.$random;
$client = new GuzzleHttp\Client;
$jar = new \GuzzleHttp\Cookie\CookieJar;
$r = $client->request('GET', $url, [
    'cookies' => $jar,
    'sink' => 'captcha_bad.jpg'
]);
$cookie = $jar->getCookieByName('CAKEPHP');
$cake = $cookie->getValue();

shell_exec('convert -colorspace gray -modulate 120 -contrast-stretch 10%x80% -modulate 140 -gaussian-blur 1 -contrast-stretch 5%x50% +repage -negate -gaussian-blur 4 -negate -modulate 130 captcha_bad.jpg captcha_good.jpg');


$cod = (new TesseractOCR('captcha_good.jpg'))->allowlist(range(0, 9), range('a', 'z'))->run();

// $cod = readline('Enter a string: ');

$request = $client->post('http://www.sintegra.fazenda.pr.gov.br/sintegra/', [
    'form_params' => [
        '_method' => 'POST',
        'data[Sintegra1][CodImage]' => $cod,
        'data[Sintegra1][Cnpj]' => '00.776.574/0001-56',
        'empresa' => 'Consultar Empresa',
        'data[Sintegra1][Cadicms]' => '',
        'data[Sintegra1][CadicmsProdutor]' => '',
        'data[Sintegra1][CnpjCpfProdutor]' => '',
    ],
	'headers' => [
        'Host' => 'www.sintegra.fazenda.pr.gov.br',
        'User-Agent' => 'Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0',
        'Accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language' => 'en-US,en;q=0.5',
        'Content-Type' => 'application/x-www-form-urlencoded',
        'Origin' => 'http://www.sintegra.fazenda.pr.gov.br',
        'Connection' => 'keep-alive',
        'Referer' => 'http://www.sintegra.fazenda.pr.gov.br/sintegra/',
        'Cookie' => 'CAKEPHP='.$cake,
        'Upgrade-Insecure-Requests' => '1',
    ]
]);

$html = $request->getBody()->getContents();
$crawler = new \Symfony\Component\DomCrawler\Crawler($html);
$tb = $crawler->filter('table')->filter('tr')->each(function ($tr, $i) {
    return $tr->filter('td')->each(function ($td, $i) {
        return trim($td->text());
    });
});

print_r($tb);
