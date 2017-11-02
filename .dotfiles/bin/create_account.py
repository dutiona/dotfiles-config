#!/usr/bin/python3

import pprint
import argparse
import subprocess
import unicodedata
import sys
import getpass
import time
from datetime import datetime

class account(object):
    def __init__(self, data):
        self._data = data
        self.postcmd = []
        self._data['uidNumber'] = self.next_uidNumber()
        self._data['gidNumber'] = self.get_gidNumber()
        self._data['email'] = self.normalize("{uid}@lrde.epita.fr".format(**self._data))
        if "expire_date" in self._data and self._data['expire_date']:
            epoch = datetime(1970, 1, 1)
            expire_date = datetime.strptime(self._data['expire_date'], "%Y-%m-%d")
            delta = expire_date - epoch
            self._data['shadow_expire'] = delta.days

    def next_uidNumber(self):
        output = subprocess.check_output(["ldapsearch", "-x", "-LLL",
            "-b", self._data["base"],
            "-H", self._data["ldap_uri"],
            "(objectClass=posixAccount)",
            "uidNumber"], universal_newlines=True)
        return int(output.split("\n")[-3].split(": ")[1]) + 1

    def get_gidNumber(self):
        try:
            output = subprocess.check_output(["ldapsearch", "-x", "-LLL",
                "-b", self._data["base"],
                "-H", self._data["ldap_uri"],
                "(&(objectClass=posixGroup)(cn={gid}))".format(**self._data),
                "gidNumber"], universal_newlines=True)
            return int(output.split("\n")[1].split(": ")[1])
        except IndexError:
            print("Group '{gid}' doesn't exist".format(**self._data))
            sys.exit(1)

    def normalize(self, s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')).casefold()

    def get_ldif(self):
        ldif = []
        ldif.append("dn: uid={uid},ou=people,{base}".format(**self._data))
        ldif.append("objectClass: inetOrgPerson")
        ldif.append("objectClass: posixAccount")
        ldif.append("objectClass: postfixUser")
        if "shadow_expire" in self._data:
            ldif.append("objectClass: shadowAccount")
            ldif.append("shadowExpire: {shadow_expire}".format(**self._data))
        ldif.append("uid: {uid}".format(**self._data))
        ldif.append("uidNumber: {uidNumber}".format(**self._data))
        ldif.append("gidNumber: {gidNumber}".format(**self._data))
        ldif.append("cn: {first_name} {last_name}".format(**self._data))
        ldif.append("loginShell: {shell}".format(**self._data))
        ldif.append("mail: {email}".format(**self._data))
        ldif.append(self.normalize("mailacceptinggeneralid: {first_name}.{last_name}@lrde.epita.fr".format(**self._data).lower()))
        ldif.append(self.normalize("mailacceptinggeneralid: {last_name}.{first_name}@lrde.epita.fr".format(**self._data).lower()))
        ldif.append("sn: {last_name}".format(**self._data))
        ldif.append("givenName: {first_name}".format(**self._data))
        ldif.append("homeDirectory: {home_dir}".format(**self._data).format(**self._data))

        return "\n".join(ldif) + "\n"

    def create(self, login, password):
        ldif = self.get_ldif()

        cmd = ["ldapadd", "-x",
                "-H", self._data["ldap_uri"],
                "-D", "uid={},ou=people,{}".format(login, self._data["base"]),
                "-w", password]
        with subprocess.Popen(cmd, stdin=subprocess.PIPE, universal_newlines=True) as proc:
            proc.communicate(input=ldif)
            proc.wait()

        while(True):
            try:
                self.set_random_password(login, password)
                break
            except:
                time.sleep(1)

        self.postcmd.append("ssh kaboul /root/generate_aliases")
        self._data['nfs_dir'] = "{}".format(self._data["home_dir"]).format(**self._data).replace("lrde", "volume1", 1)
        self.postcmd.append("ssh nfs mkdir -p {nfs_dir}".format(**self._data))
        self.postcmd.append("ssh nfs chown {uidNumber}:{gidNumber} {nfs_dir}".format(**self._data))
        self.postcmd.append("ssh nfs chmod 700 {nfs_dir}".format(**self._data))

    def set_random_password(self, login, password):
        random_password = subprocess.check_output(["pwgen", "-ncB", "8", "1"], universal_newlines=True)
        self._data["password"] = random_password[:-1] # remove '\n'

        cmd = ["ldappasswd", "-x",
                "-H", self._data["ldap_uri"],
                "-D", "uid={},ou=people,{}".format(login, self._data["base"]),
                "-w", password,
                "-s", self._data["password"],
                "uid={uid},ou=people,{base}".format(**self._data)]
        subprocess.check_call(cmd)


    # echo "# to execute on nfs.lrde.epita.fr"
    # echo "mkdir /volume1/home/$group/$uid"
    # echo "chown $uidNumber:$gidNumber /volume1/home/$group/$uid"
    # echo "chmod 700 /volume1/home/$group/$uid"
    # echo "# to execute on kaboul.lrde.epita.fr"
    # echo "/root/generate_aliases"
    # echo "------------------------------"


    def __str__(self):
        s = []
        s.append("Nom:      {first_name} {last_name}".format(**self._data))
        s.append("Login:    {uid}".format(**self._data))
        s.append("Password: {password}".format(**self._data))
        s.append("Email:    {email}".format(**self._data))
        return "\n".join(s)



def main():
    parser = argparse.ArgumentParser(description="Create a new LDAP user in the LRDE LDAP server")
    # Account
    parser.add_argument('-u', '--uid', required=True)
    parser.add_argument('-g', '--gid', required=True)
    parser.add_argument('-f', '--first-name', required=True)
    parser.add_argument('-l', '--last-name', required=True)
    parser.add_argument('-d', '--home-dir', default='/lrde/home/{uid}', help='User home directory (default to /lrde/home/{uid})')
    parser.add_argument('-e', '--expire-date', help='The date on which the user account will be disabled (set shadowExpire attribute)')
    parser.add_argument('-s', '--shell', default='/bin/bash', help='Default user shell (default to /bin/bash)')

    # LDAP arguments
    parser.add_argument('-b', '--base', default='dc=lrde,dc=epita,dc=fr')
    parser.add_argument('-H', '--ldap-uri', default='ldaps://ldap.lrde.epita.fr')

    # Misc
    parser.add_argument('-n', '--dry-run', action='store_true', help='Perform a trial run with no changes made')

    args = parser.parse_args()

    login = input("Login: ")
    password = getpass.getpass()

    # print(vars(args))
    acc = account(vars(args))
    acc.create(login, password)
    print(acc)
    print("-- post commands --")
    print("\n".join(acc.postcmd))

if __name__ == '__main__':
    main()
