#!/usr/bin/python3

import argparse
import csv
import getpass
import time

import create_account

def process_csv(args, login, password):
    postcmds = set()
    with open(args.csv) as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            data = {}
            data.update(vars(args))
            data.update(row)
            acc = create_account.account(data)
            acc.create(login, password)

            print(acc)
            print()
            postcmds |= set(acc.postcmd)
            time.sleep(1)
    print("-- post commands --")
    print("\n".join(postcmds))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True)
    parser.add_argument('-g', '--gid', required=True)
    parser.add_argument('-d', '--home-dir', default='/lrde/home/{uid}', help='User home directory (default to /lrde/home/{uid})')
    parser.add_argument('-e', '--expire-date', help='The date (Y-m-d) on which the user account will be disabled (set shadowExpire attribute)')
    parser.add_argument('-s', '--shell', default='/bin/zsh', help='Default user shell (default to /bin/bash)')

    # LDAP arguments
    parser.add_argument('-b', '--base', default='dc=lrde,dc=epita,dc=fr')
    parser.add_argument('-H', '--ldap-uri', default='ldaps://ldap.lrde.epita.fr')

    # Misc
    parser.add_argument('-n', '--dry-run', default=False, action='store_true', help='Perform a trial run with no changes made')

    args = parser.parse_args()

    login = input("Login: ")
    password = getpass.getpass()

    if args.csv:
        process_csv(args, login, password)

if __name__ == '__main__':
    main()
