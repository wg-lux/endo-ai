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

v = Video.objects.first()
v_sm = v.sensitive_meta
v_pat = v.patient

rf = ReportFile.objects.first()
rf_sm = rf.sensitive_meta
rf_pat = rf.patient

ic(f"First RawVideoFile: {rvf}")
ic(f"Sensitive Metadata: {rvf_sm}")
ic(f"Video belongs to Pseudo-Patient: {rvf_pat}")

#
ic(f"First RawPdfFile: {rpf}")
ic(f"Sensitive Metadata Metadata: {rpf_sm}")
ic(f"Report belongs to Pseudo-Patient: {rpf_pat}")

ic(f"First Video: {v}")
ic(f"Sensitive Metadata: {v_sm}")
ic(f"Video belongs to Pseudo-Patient: {v_pat}")

ic(f"First ReportFile: {rf}")
ic(f"Sensitive Metadata: {rf_sm}")
ic(f"Report belongs to Pseudo-Patient: {rf_pat}")

lrvs = rvf.label_video_segments.all()
ic(f"RawVideoFile has {len(lrvs)} LabelVideoSegments")

lvs = v.label_video_segments.all()
ic(f"Video has {len(lvs)} LabelVideoSegments")
