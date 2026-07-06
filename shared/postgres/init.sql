-- Bootstrap: one role + one database per service.
-- Each service can only connect to its own database (API-only rule,
-- enforced physically).

CREATE ROLE user_service LOGIN PASSWORD 'user_service_pw';
CREATE DATABASE users_db OWNER user_service;
REVOKE CONNECT ON DATABASE users_db FROM PUBLIC;

CREATE ROLE post_service LOGIN PASSWORD 'post_service_pw';
CREATE DATABASE posts_db OWNER post_service;
REVOKE CONNECT ON DATABASE posts_db FROM PUBLIC;

-- Dedicated test databases so pytest never touches dev data.
CREATE DATABASE users_test_db OWNER user_service;
REVOKE CONNECT ON DATABASE users_test_db FROM PUBLIC;
CREATE DATABASE posts_test_db OWNER post_service;
REVOKE CONNECT ON DATABASE posts_test_db FROM PUBLIC;
