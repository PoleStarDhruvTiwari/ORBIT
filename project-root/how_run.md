whenever any isssue with database : 

docker exec -i project-root-postgres-1 psql -U postgres -c "DROP DATABASE IF EXISTS shiftdb;"
docker exec -i project-root-postgres-1 psql -U postgres -c "CREATE DATABASE shiftdb;"
Get-Content "C:\Users\91964\Desktop\ORBIT_Perfect\project-root\backend\sql\schema.sql" | docker exec -i project-root-postgres-1 psql -U postgres -d shiftdb
Get-Content "C:\Users\91964\Desktop\ORBIT_Perfect\project-root\backend\sql\seed.sql" | docker exec -i project-root-postgres-1 psql -U postgres -d shiftdb

run this command 