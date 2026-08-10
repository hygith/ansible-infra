#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import os

DOCUMENTATION = r'''
---
module: create_testing_file
short_description: Creates testing.txt in /home/admin without root privileges
description:
  - Ensures /home/admin/testing.txt exists with specified content and file permissions.
options:
  dest:
    description: Absolute path of the destination file.
    type: str
    default: /home/admin/testing.txt
  content:
    description: The text content to write to the file.
    type: str
    default: "This file was created by Ansible.\n"
  mode:
    description: File permissions in octal format string (e.g., '0644').
    type: str
    default: '0644'
'''

EXAMPLES = r'''
- name: Create testing.txt with default content
  create_testing_file:

- name: Create testing.txt with custom parameters
  create_testing_file:
    dest: /home/admin/testing.txt
    content: "This file was created by Ansible.\n"
    mode: '0644'
'''

def run_module():
    # Define arguments mirroring built-in options
    module_args = dict(
        dest=dict(type='str', required=False, default='/home/admin/testing.txt'),
        content=dict(type='str', required=False, default='This file was created by Ansible.\n'),
        mode=dict(type='str', required=False, default='0644')
    )

    result = dict(
        changed=False,
        dest='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    dest_path = module.params['dest']
    content = module.params['content']
    mode_str = module.params['mode']

    result['dest'] = dest_path

    # Parse octal mode string (e.g., '0644' -> 0o644)
    try:
        mode_int = int(mode_str, 8)
    except ValueError:
        module.fail_json(msg=f"Invalid octal mode string: {mode_str}", **result)

    file_exists = os.path.isfile(dest_path)
    current_content = ""
    current_mode = None

    if file_exists:
        try:
            with open(dest_path, 'r') as f:
                current_content = f.read()
            # Retrieve octal permissions for current file
            current_mode = os.stat(dest_path).st_mode & 0o777
        except OSError as e:
            module.fail_json(msg=f"Failed to read file attributes: {str(e)}", **result)

    # Determine if changes are needed (content or mode)
    content_changed = (not file_exists) or (current_content != content)
    mode_changed = (not file_exists) or (current_mode != mode_int)

    if content_changed or mode_changed:
        result['changed'] = True

        # Handle dry-run (--check)
        if module.check_mode:
            module.exit_json(**result)

        try:
            # Write content
            with open(dest_path, 'w') as f:
                f.write(content)

            # Apply permissions
            os.chmod(dest_path, mode_int)

            result['message'] = f"Successfully updated {dest_path}"
        except OSError as e:
            module.fail_json(msg=f"Failed writing or setting permissions on {dest_path}: {str(e)}", **result)
    else:
        result['message'] = f"{dest_path} is up to date"

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
