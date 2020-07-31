#!/usr/bin/env python3
import os
import sys
# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument("--vault-id", type=str)
# args = parser.parse_args()

# if args.vault_id is None or args.vault_id == "None" or args.vault_id == "default":

envvar_vault_pass = "VAULT_PASSWORD_BUILDENV"

if os.environ.get(envvar_vault_pass) is not None and os.environ.get(envvar_vault_pass) != "":
    print(os.environ[envvar_vault_pass])
else:
    print("ERROR: '" + envvar_vault_pass + "' is not set in environment")
    sys.exit(1)
