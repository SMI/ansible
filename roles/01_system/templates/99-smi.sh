#!/bin/sh
# {{ ansible_managed }}

printf "#\n"
printf "# {{ inventory_hostname }}\n"
printf "# {{ hostvars[inventory_hostname]['host_role'] }}\n"
printf "#\n"
printf "# This host is managed by SMI's Ansible playbook\n"
printf "# Contact email: {{ smi_system_contact_email }}\n"
printf "#\n"
