from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.parsing.vault import VaultLib, VaultSecret
import re


class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        if 'vaultid' not in self._task.args or 'vaultpass' not in self._task.args or 'action' not in self._task.args:
            return {"failed": True, "msg": "'vaultid' and 'vaultpass' and 'action' are required options"}

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp is deprecated

        if self._task.args["action"] == "encrypt":
            if "plaintext" not in self._task.args:
                return {"failed": True, "msg": "'plaintext' is required for encrypt"}

            # encrypt:
            oVaultSecret = VaultSecret(self._task.args["vaultpass"].encode('utf-8'))
            oVaultLib = VaultLib([(self._task.args["vaultid"], oVaultSecret)])
            vault_tag = oVaultLib.encrypt(self._task.args["plaintext"], oVaultSecret, self._task.args["vaultid"])

            # reformat output
            g_tag_value = re.match(r"^(?P<header>\$ANSIBLE_VAULT;(?P<ver>[\d\.]+?);(?P<cipher>\w+?)(?:;(?P<vault_id>.*?))?)[\r\n](?P<vaulttext_raw>.*)$", vault_tag, flags=re.DOTALL)
            res_cipherstr = re.sub(r'[ \n\r]', "", g_tag_value.group('vaulttext_raw'), flags=re.DOTALL)
            res_vaulttext = g_tag_value.group('header') + "\n" + res_cipherstr

            result['msg'] = {"res_vaulttext": res_vaulttext, "plaintext": self._task.args["plaintext"]}

        else:
            if "vaulttext" not in self._task.args:
                return {"failed": True, "msg": "'vaulttext' is required for decrypt"}

            oVaultLib = VaultLib([(self._task.args["vaultid"], VaultSecret(self._task.args["vaultpass"].encode('utf-8')))])
            plaintext = oVaultLib.decrypt(self._task.args["vaulttext"])
            result['msg'] = {"res_vaulttext": self._task.args["vaulttext"], "plaintext": plaintext}

        result['failed'] = False

        return result
