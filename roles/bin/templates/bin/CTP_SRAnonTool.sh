#!/bin/bash
# {{ ansible_managed }}
# CTP_SRAnonTool.sh
#   This script is called from CTP via the SRAnonTool config in the SmiServices config
# It is called with -i DICOMfile -o OutputDICOMfile
# It extracts the text from DICOMfile, passes it through the SemEHR anonymiser,
# and reconstructs the structured text into OutputDICOMfile.
# NOTE: the -o file must already exist! because only the text part is updated.
# NOTE: semehr needs python2 but all other tools need python3.
# XXX TODO: copy the input to the output if it doesn't exist?

prog=$(basename "${0%.*}")
usage="usage: ${prog} [-d] [-v] [-e virtualenv] [-s semehr_root] -i read_from.dcm  -o write_into.dcm"
options="dve:s:i:o:"
semehr_dir="${SMI_SEMEHR_TEMP_DIR:-/tmp/semehr}"
virtenv=""
debug=0
verbose=0

# shellcheck disable=SC2154
if [[ "${SMI_ENV_DIR}" == "" ]]; then
	echo "${prog}: ERROR: env var SMI_ENV_DIR must be set" >&2
    exit 1
fi

PYTHON="${SMI_ENV_DIR}/venvs/semehr/bin/python"
if [[ ! -f "${PYTHON}" ]]; then
	echo "${prog}: ERROR: Expected to find python at ${PYTHON}" >&2
    exit 1
fi

# shellcheck disable=SC2154
if [[ "${SMI_STRUCTUREDREPORTS_APPLICATIONS_DIR}" == "" ]]; then
	echo "${prog}: ERROR: env var SMI_STRUCTUREDREPORTS_APPLICATIONS_DIR must be set" >&2
    exit 1
fi

# shellcheck disable=SC2154
if [[ "${SMI_STRUCTUREDREPORTS_SEMEHR_ANON_TASK}" == "" ]]; then
	echo "${prog}: ERROR: env var SMI_STRUCTUREDREPORTS_SEMEHR_ANON_TASK must be set" >&2
    exit 1
fi

# shellcheck disable=SC2154
if [[ "${SMI_LOGS_ROOT}" == "" ]]; then
	echo "${prog}: ERROR: env var SMI_LOGS_ROOT must be set" >&2
    exit 1
fi


# Configure logging
log="${SMI_LOGS_ROOT}/${prog}/${prog}.log"
mkdir -p "$(dirname "\"""${log}""\"")"
touch "${log}"
date=$(date)
echo "${date} $*" >> "${log}"

# Error reporting and exit
tidy_exit()
{
	rc=$1
	msg="$2"
	echo "${msg}" >&2
	date=$(date)
	echo "${date} ${msg}" >> "${log}"
	# Tidy up, if not debugging
	if [[ "${debug}" -eq 0 ]]; then
	  if [[ -f "${input_doc}" ]]; then rm -f "${input_doc}"; fi
	  if [[ -f "${anon_doc}" ]]; then rm -f "${anon_doc}"; fi
	  if [[ -f "${anon_xml}" ]]; then rm -f "${anon_xml}"; fi
	  # Prefer not to use rm -fr for safety
	  if [[ -d "${semehr_input_dir}" ]]; then rm -f "${semehr_input_dir}/"*; fi
	  if [[ -d "${semehr_input_dir}" ]]; then rmdir "${semehr_input_dir}"; fi
	  if [[ -d "${semehr_output_dir}" ]]; then rm -f "${semehr_output_dir}/"*; fi
	  if [[ -d "${semehr_output_dir}" ]]; then rmdir "${semehr_output_dir}"; fi
	fi
	# Tell user where log file is when failure occurs
	if [[ "${rc}" -ne 0 ]]; then echo "See log file ${log}" >&2; fi
	exit "${rc}"
}

# Command line arguments
while getopts "${options}" var; do
case "${var}" in
	d) debug=1;;
	v) verbose=1;;
	e) virtenv="${OPTARG}";;
	i) input_dcm="${OPTARG}";;
	o) output_dcm="${OPTARG}";;
	s) semehr_dir="${OPTARG}";;
	*) echo "${usage}" >&2; exit 1;;
esac
done
shift $((OPTIND - 1))

if [[ ! -f "${input_dcm}" ]]; then
	tidy_exit 2 "ERROR: cannot read input file '${input_dcm}'"
fi
if [[ ! -f "${output_dcm}" ]]; then
	tidy_exit 3 "ERROR: cannot write to ${output_dcm} because it must already exist"
fi

# Activate the virtual environment
if [[ "${virtenv}" != "" ]]; then
	if [[ -f "${virtenv}/bin/activate" ]]; then
		# Can't shellcheck the Venv script, it isn't ours
		# shellcheck disable=SC1091
		source "${virtenv}/bin/activate"
	else
		echo "ERROR: Cannot activate virtual environment ${virtenv} - no bin/activate script" >&2
		exit 1
	fi
fi

# ---------------------------------------------------------------------
# Determine the SemEHR filenames - create per-process directories
semehr_input_dir=$(mktemp  -d -t input_docs.XXXX --tmpdir="${semehr_dir}")
semehr_output_dir=$(mktemp -d -t anonymised.XXXX --tmpdir="${semehr_dir}")
if [[ "${semehr_input_dir}" == "" ]]; then
	tidy_exit 8 "Cannot create temporary directory in ${semehr_dir}"
fi
if [[ "${semehr_output_dir}" == "" ]]; then
	tidy_exit 9 "Cannot create temporary directory in ${semehr_dir}"
fi

doc_filename=$(basename "${input_dcm}")
input_doc="${semehr_input_dir}/${doc_filename}"
anon_doc="${semehr_output_dir}/${doc_filename}"
anon_xml="${semehr_output_dir}/${doc_filename}.knowtator.xml"

# ---------------------------------------------------------------------
# Convert DICOM to text
#  Reads  $input_dcm
#  Writes $input_doc
if [[ "${verbose}" -gt 0 ]]; then
	echo "RUN: CTP_DicomToText.py -i ${input_dcm} -o ${input_dcm}.SRtext"
fi
${PYTHON} "${SMI_STRUCTUREDREPORTS_APPLICATIONS_DIR}/SRAnonTool/CTP_DicomToText.py" \
	-i "${input_dcm}" \
	-o "${input_doc}"  || tidy_exit 4 "Error $? from CTP_DicomToText.py while converting ${input_dcm} to ${input_doc}"

# ---------------------------------------------------------------------
# Run the SemEHR anonymiser using a set of private directories
#  Reads  $input_doc
#  Writes $anon_doc, and $anon_xml via the --xml option
#
${PYTHON} "${SMI_STRUCTUREDREPORTS_APPLICATIONS_DIR}/semehr_anon.py" -c "${SMI_STRUCTUREDREPORTS_SEMEHR_ANON_TASK}" -i "${input_doc}" -o "${anon_doc}" --xml || tidy_exit 5 "Error running SemEHR-anon given ${input_doc} from ${input_dcm}"
# If there's still no XML file then exit
if [[ ! -f "${anon_xml}" ]]; then
	tidy_exit 6 "ERROR: SemEHR-anon failed to convert ${input_doc} to ${anon_xml}"
fi

# ---------------------------------------------------------------------
# Convert XML back to DICOM
#  Reads  $input_dcm and $anon_xml
#  Writes $output_dcm (must already exist)
if [[ "${verbose}" -gt 0 ]]; then
	echo "RUN: CTP_XMLToDicom.py -i ${input_dcm} -x ${anon_xml} -o ${output_dcm}"
fi
${PYTHON} "${SMI_STRUCTUREDREPORTS_APPLICATIONS_DIR}/SRAnonTool/CTP_XMLToDicom.py" \
	-i "${input_dcm}" \
	-x "${anon_xml}" \
	-o "${output_dcm}"   || tidy_exit 7 "Error $? from CTP_XMLToDicom.py while redacting ${output_dcm} with ${anon_xml}"

tidy_exit 0 "Finished with ${input_dcm}"
