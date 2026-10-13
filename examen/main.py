
din verificator importă build_url , is_https , show_response , check_site , scan_sites , check_headers , retry_check

 print ( "=== Partea 1: Funcții ajutătoare ===" )
 print ( "build_url (fără bară):" , build_url ( " example.com " , "login" ))
 print ( "build_url (cu bară):" , build_url ( " example.com " , "/login" ))
 print ( "is_https (valid):" , is_https ( " https://example.com " ))
 print ( "is_https (invalid):" , is_https ( " http://example.com " ))

 print ( " \n === Partea 2: show_response ===" )
 print ( "Caz care merge ( https://example.com ):" )
 show_response ( " https://example.com " )
 print ( " \n Caz care eșuează (domeniu inexistent):" )
 show_response ( " http://this-site-does-not-exist.invalid " )

 print ( " \n === Partea 3: check_site ===" )
 print ( "Caz care merge:" , check_site ( " https://example.com " ))
 print ( "Caz care eșuează:" , check_site ( " http://this-site-does-not-exist.invalid " ))

 print ( " \n === Partea 4: scan_sites ===" )
 scan_sites ()

 tipărire ( " \n === Partea 5: check_headers ===" )
 print ( "Caz cu anteturi prezente (parțial):" , check_headers ( " https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff " ))
 print ( "Caz care eșuează la conectare:" , check_headers ( " http://this-site-does-not-exist.invalid " ))

 print ( " \n === Partea 6: retry_check ===" )
 print ( "Caz eroare 404 (se oprește din prima):" , retry_check ( " https://httpbin.org/status/404 " ))
 print ( "Caz eroare server 500 (încearcă de 3 ori):" , retry_check ( " https://httpbin.org/status/500 " ))
 print ( "Caz limită 500 cu 2 încercări:" , retry_check ( " https://httpbin.org/status/500 " , attempts = 2 ))
 print ( "Caz conexiune picată:" , retry_check ( " http://this-site-does-not-exist.invalid " ))
