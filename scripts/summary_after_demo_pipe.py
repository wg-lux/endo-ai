import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "endo_ai.settings_dev")
django.setup()

from endoreg_db.models import RawVideoFile, RawPdfFile, Video, ReportFile
from icecream import ic

rvf = RawVideoFile.objects.first()
rvf_pat = rvf.patient
rvf_sm = rvf.sensitive_meta

rpf = RawPdfFile.objects.first()
rpf_sm = rpf.sensitive_meta
rpf_pat = rpf.patient

ic(f"First RawVideoFile: {rvf}")
ic(f"Sensitive Metadata: {rvf_sm}")
ic(f"Video belongs to Pseudo-Patient: {rvf_pat}")
#
ic(f"First RawPdfFile: {rpf}")
ic(f"Sensitive Metadata Metadata: {rpf_sm}")
ic(f"Report belongs to Pseudo-Patient: {rpf_pat}")
