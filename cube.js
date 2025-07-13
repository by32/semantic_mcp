module.exports = {
  dbType: ({ dataSource }) => 'duckdb',
  driverFactory: ({ dataSource }) => {
    return {
      type: 'duckdb',
      database: process.env.CUBEJS_DB_DUCKDB_DATABASE_PATH || './lake_data/warehouse.db'
    };
  }
};