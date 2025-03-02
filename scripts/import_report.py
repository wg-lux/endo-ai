from agl_report_reader.report_reader import ReportReader
from icecream import ic

GASTRO_REPORT_PATH = "data/import/report/report.pdf"

rr = ReportReader()
text, anonymized_text, report_meta = rr.process_report(GASTRO_REPORT_PATH)

ic(f"Text: {text}")
ic(f"Anonymized Text: {anonymized_text}")
ic(f"Report Meta: {report_meta}")
