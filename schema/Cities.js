cube(`Cities`, {
  sql: `SELECT * FROM cities`,
  
  dimensions: {
    id: {
      sql: `id`,
      type: `number`,
      primaryKey: true
    },
    
    cityName: {
      sql: `city_name`,
      type: `string`
    },
    
    stateName: {
      sql: `state_name`,
      type: `string`
    },
    
    region: {
      sql: `region`,
      type: `string`
    }
  },
  
  measures: {
    count: {
      type: `count`
    },
    
    totalPopulation: {
      sql: `population`,
      type: `sum`
    }
  }
});
EOF < /dev/null