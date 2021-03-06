#!/bin/bash
# csr.sh: Certificate Signing Request Generator
# Copyright(c) 2005 Evaldo Gardenali <evaldo@gardenali.biz>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the author nor the names of its contributors may
#    be used to endorse or promote products derived from this software
#    without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
#
# ChangeLog:
# Mon May 23 00:14:37 BRT 2005 - evaldo - Initial Release

# be safe about permissions
LASTUMASK=`umask`
umask 077

# OpenSSL for HPUX needs a random file
RANDOMFILE=$HOME/.rnd

# create a config file for openssl
CONFIG=`mktemp -q /tmp/openssl-conf.XXXXXXXX`
if [ ! $? -eq 0 ]; then
    echo "Could not create temporary config file. exiting"
    exit 1
fi

printf "Short Hostname (ie. imap big_srv www2): "
read HOST
printf "FQDN/CommonName (ie. www.example.com) : "
read COMMONNAME

echo "Type SubjectAltNames for the certificate, one per line. Enter a blank line to finish"
SAN=1        # bogus value to begin the loop
SANAMES=""   # sanitize
while [ ! "$SAN" = "" ]; do
    printf "SubjectAltName: DNS:"
    read SAN
    if [ "$SAN" = "" ]; then break; fi # end of input
    if [ "$SANAMES" = "" ]; then
        SANAMES="DNS:$SAN"
    else
        SANAMES="$SANAMES,DNS:$SAN"
    fi
done

# Config File Generation

cat <<EOF > $CONFIG
# -------------- BEGIN custom openssl.cnf -----
 HOME                    = $PWD
EOF

if [ "`uname -s`" = "HP-UX" ]; then
    echo " RANDFILE                = $RANDOMFILE" >> $CONFIG
fi

cat <<EOF >> $CONFIG
 oid_section             = new_oids
 [ new_oids ]
 [ req ]
 default_days            = 3650            # how long to certify for
 default_keyfile         = ${HOST}_privatekey.pem
 distinguished_name      = req_distinguished_name
 encrypt_key             = no
 string_mask = nombstr
EOF

if [ ! "$SANAMES" = "" ]; then
    echo "req_extensions = v3_req # Extensions to add to certificate request" >> $CONFIG
fi

cat <<EOF >> $CONFIG
 [ req_distinguished_name ]
 countryName			= Country Name (2 letter code)
 countryName_default		= FR
 countryName_min		= 2
 countryName_max		= 2

 stateOrProvinceName		= State or Province Name (full name)
 stateOrProvinceName_default	= Ile de France

 localityName			= Locality Name (eg, city)
 localityName_default		= Kremlin-Bicetre

 0.organizationName		= Organization Name (eg, company)
 0.organizationName_default	= EPITA

 organizationalUnitName		= Organizational Unit Name (eg, section)
 organizationalUnitName_default	= LRDE

 commonName              = Common Name (eg, YOUR name)
 commonName_default      = $COMMONNAME
 commonName_max          = 64

 emailAddress			= Email Address
 emailAddress_max		= 64
 emailAddress_default		= admin@lrde.epita.fr

 [ v3_req ]
EOF

if [ ! "$SANAMES" = "" ]; then
    echo "subjectAltName=$SANAMES" >> $CONFIG
fi

echo "# -------------- END custom openssl.cnf -----" >> $CONFIG

echo "Running OpenSSL..."
if [[ ! -f ${HOST}_privatekey.pem ]]; then
    NEWKEY="-newkey rsa:2048"
fi
openssl req -batch -config $CONFIG $NEWKEY -out ${HOST}_csr.pem

rm $CONFIG
umask $LASTUMASK
