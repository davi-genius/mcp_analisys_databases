CREATE USER petclinic WITH PASSWORD 'petclinic';

CREATE DATABASE petclinic
    WITH
    OWNER = petclinic
    ENCODING = 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8' 
    LC_CTYPE = 'pt_BR.UTF-8'
    TABLESPACE = pg_default;
    
GRANT ALL PRIVILEGES ON DATABASE petclinic TO petclinic;