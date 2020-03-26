from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
from ansible.module_utils._text import to_native, to_text
from os import path, listdir

class ActionModule(ActionBase):

    VALID_ARGUMENTS = [ 'from', 'ignore_missing_files' ]

    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        for arg in self._task.args:
            if not arg in self.VALID_ARGUMENTS:
                raise AnsibleError('%s is not a valid option in merge_vars' % arg)

        self.ignore_missing_files = self._task.args.get('ignore_missing_files', False)

        self.show_content = True;
        self._task.action = 'include_vars';

        failed = False

        files = []
        for source in self._task.args['from']:
            if path.isfile(source):
                files.append(source)
            elif not path.isfile(source) and self.ignore_missing_files:
                continue
            elif path.isdir(source):
                dirfiles = [path.join(source, filename) for filename in listdir(source)]
                dirfiles.sort()
                files.append(dirfiles)
            elif not path.isdir(source) and self.ignore_missing_files:
                continue
            else:
                failed = True
                err_msg = to_native('%s does not exist' % source)
                break

        data = {}
        if not failed:
            for filename in files:
                try:
                    data = merge_hash(data, self._load_from_file(filename))

                except AnsibleError as e:
                    failed = True
                    err_msg = to_native(e)

        result = super(ActionModule, self).run(task_vars=task_vars)

        if failed:
            result['failed'] = failed
            result['message'] = err_msg

        result['ansible_included_var_files'] = files
        result['ansible_facts'] = data
        result['_ansible_no_log'] = not self.show_content
        
        return result

    def _load_from_file(self, filename):
        # this is the approach used by include_vars in order to get the show_content
        # value based on whether decryption occured.  load_from_file does not return
        # that value. 
        #    https://github.com/ansible/ansible/blob/v2.7.5/lib/ansible/plugins/action/include_vars.py#L236-L240
        b_data, show_content = self._loader._get_file_contents(filename)
        data = to_text(b_data, errors='surrogate_or_strict')

        self.show_content = show_content
        return self._loader.load(data, file_name=filename, show_content=show_content) or {}
