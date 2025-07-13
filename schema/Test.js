cube('Test', {
  sql: 'SELECT 1 as id, \'test\' as name',
  
  dimensions: {
    name: {
      sql: 'name',
      type: 'string'
    }
  },
  
  measures: {
    count: {
      type: 'count'
    }
  }
});