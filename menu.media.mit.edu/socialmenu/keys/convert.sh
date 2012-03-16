#!/bin/sh

openssl pkcs12 -clcerts -nokeys -out cert.pem -in APSDevCertificate.p12
openssl pkcs12 -nocerts -out key.pem -in DaweiDooleyPrivateKey.p12
openssl rsa -in key.pem -out key.unencrypted.pem
cat key.unencrypted.pem cert.pem > iphone_ck.pem

openssl pkcs12 -clcerts -nokeys -out prodcert.pem -in APSProdCertificate.p12
cat key.unencrypted.pem prodcert.pem > iphone_live.pem

#openssl x509 -in aps_developer_identity.cer -inform DER -outform PEM -out cert.pem
#openssl pkcs12 -in DaweiDooleyPrivateKey.p12 -out key.pem -nodes
#cat key.pem cert.pem > iphone_ck.pem
#openssl x509 -in aps_production_identity.cer -inform DER -outform PEM -out prodcert.pem
#cat key.pem prodcert.pem > iphone_live.pem

