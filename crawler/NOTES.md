## Notes

### Postgres

Useful commands:

- Run shell: `psql`
- List all databases: `\list`
- List all tables in current database: `\d` or `\d+` for expanded view
- Create a new table: `CREATE TABLE person (name text, age int, birth_date date);`
- Show columns of given table: `\d person`
- Insert a row into table: `INSERT INTO person VALUES (23, 'Assil', date '1993-12-19');`
- Show first 10 rows in a table: `SELECT * FROM person LIMIT 10;`
