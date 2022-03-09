connect-db:
	PGPASSWORD=biotisst_password psql -h localhost -U biotisst_admin biotisst_db -p 15432

run:
	python manage.py runserver