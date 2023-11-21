# {{ ansible_managed }}

# shellcheck source=/dev/null
source "{{ smi_service_software_install_dir }}/configs/env.bash"

export SMI_SMISERVICES_VERSION="5.4.0"
export SMI_LOGS_ROOT="{{ smi_service_software_logs_dir }}/{{ config_name }}"
