#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: usermod
short_description: Manage users using clish commands
description:
  - Locks database override, creates users, sets password hashes, and assigns RBA roles using clish CLI commands.
options:
  name:
    description: Name of the user to manage.
    type: str
    required: true
  uid:
    description: Numeric User ID.
    type: int
    default: 0
  homedir:
    description: Path to the user's home directory.
    type: str
  password_hash:
    description: Password hash string for the user.
    type: str
  role:
    description: RBA role assigned to the user.
    type: str
    default: adminRole
  state:
    description: Target state for the user.
    type: str
    choices: [ present ]
    default: present
author:
  - System Administrator
'''

EXAMPLES = r'''
- name: Create a user with clish
  usermod:
    name: hyad
    uid: 0
    homedir: /home/hyad/
    password_hash: '$6$rounds=10000$RBzfkpHeon9Nf0BW$dIz4SrcFMbHbf7wIVrKumQikI1pE6Azjid14wVoaZc5/frNkBA1HP1mKPbf5E8u8c0djZh3PB2PzJVk8R.Uxf1'
    role: adminRole
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        uid=dict(type='int', default=0),
        homedir=dict(type='str', required=False),
        password_hash=dict(type='str', required=False, no_log=True),
        role=dict(type='str', default='adminRole'),
        state=dict(type='str', default='present', choices=['present'])
    )

    result = dict(
        changed=False,
        username='',
        executed_commands=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    username = module.params['name']
    uid = module.params['uid']
    homedir = module.params['homedir'] or f"/home/{username}/"
    password_hash = module.params['password_hash']
    role = module.params['role']

    result['username'] = username

    # Construct clish commands in sequence
    commands = [
        "clish -c 'lock database override'",
        f"clish -c 'add user {username} uid {uid} homedir {homedir}'"
    ]

    if password_hash:
        commands.append(f"clish -c 'set user {username} password-hash {password_hash}'")

    if role:
        commands.append(f"clish -c 'add rba user {username} roles {role}'")

    # Handle check mode
    if module.check_mode:
        result['executed_commands'] = commands
        module.exit_json(**result)

    # Execute commands in sequence
    for cmd in commands:
        rc, out, err = module.run_command(cmd, use_unsafe_shell=True)
        if rc != 0:
            module.fail_json(
                msg=f"Failed executing command: {cmd}",
                rc=rc,
                stdout=out,
                stderr=err
            )

        result['executed_commands'].append(cmd)

    result['changed'] = True
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
