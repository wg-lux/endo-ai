rm db.sqlite3
init-env
echo "migrate"
python manage.py migrate

echo "load db data"
python manage.py load_base_db_data

echo "load model"
python manage.py create_multilabel_model_meta --model_path "~/test-data/model/colo_segmentation_RegNetX800MF_6.ckpt"

echo "import Report"
python manage.py import_report ~/test-data/report/lux-gastro-report.pdf

echo "import Video"
python manage.py import_video ~/test-data/video/lux-gastro-video.mp4

echo "predict"
python manage.py predict_raw_video_files

echo "create pseudo patients"
python manage.py create_pseudo_patients # Use SensitiveMeta to create Patient

echo "create pseudo examinations"
python manage.py create_pseudo_examinations # Use Sensitive Meta to create Patient Examination

echo "create report File Objects"
python manage.py create_anonym_reports

echo "create video File Objects"
python manage.py create_anonym_videos

echo "print patients"
python manage.py export_patients