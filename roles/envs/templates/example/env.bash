# {{ ansible_managed }}
# Sample env file

export SMI_SMISERVICES_VERSION="v5.6.1"
export SMI_SMISERVICES_BIN="{{ envs_smi_root_dir }}/software/SMI/SmiServices/${SMI_SMISERVICES_VERSION}/smi/smi"
export SMI_SMISERVICES_EXTRACT_PIPELINE_CONFIG="smi-services-extract-pipeline.yaml"
export SMI_SMISERVICES_CTP_JAR="{{ envs_smi_root_dir }}/software/SMI/SmiServices/${SMI_SMISERVICES_VERSION}/CTPAnonymiser.jar"
