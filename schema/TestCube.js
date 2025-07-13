cube(`TestCube`, {
  sql: `SELECT * FROM cities`,
  
  dimensions: {
    cityName: {
      sql: `city_name`,
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