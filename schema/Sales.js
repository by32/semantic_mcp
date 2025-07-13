cube(`Sales`, {
  sql: `SELECT * FROM sales`,
  
  dimensions: {
    id: {
      sql: `id`,
      type: `number`,
      primaryKey: true,
      shown: false
    },
    
    transactionDate: {
      sql: `date`,
      type: `time`
    },
    
    channel: {
      sql: `channel`,
      type: `string`
    },
    
    paymentMethod: {
      sql: `payment_method`,
      type: `string`
    },
    
    customerType: {
      sql: `(SELECT customer_type FROM customers WHERE customers.id = ${CUBE}.customer_id)`,
      type: `string`
    },
    
    productCategory: {
      sql: `(SELECT category FROM products WHERE products.id = ${CUBE}.product_id)`,
      type: `string`
    },
    
    productSubcategory: {
      sql: `(SELECT subcategory FROM products WHERE products.id = ${CUBE}.product_id)`,
      type: `string`
    },
    
    brand: {
      sql: `(SELECT brand FROM products WHERE products.id = ${CUBE}.product_id)`,
      type: `string`
    },
    
    cityName: {
      sql: `(SELECT city_name FROM cities WHERE cities.id = ${CUBE}.city_id)`,
      type: `string`
    },
    
    state: {
      sql: `(SELECT state_abrv FROM cities WHERE cities.id = ${CUBE}.city_id)`,
      type: `string`
    },
    
    region: {
      sql: `(SELECT region FROM cities WHERE cities.id = ${CUBE}.city_id)`,
      type: `string`
    },
    
    salesRepName: {
      sql: `(SELECT rep_name FROM sales_reps WHERE sales_reps.id = ${CUBE}.sales_rep_id)`,
      type: `string`
    },
    
    repTerritory: {
      sql: `(SELECT territory_region FROM sales_reps WHERE sales_reps.id = ${CUBE}.sales_rep_id)`,
      type: `string`
    },
    
    repPerformanceTier: {
      sql: `(SELECT performance_tier FROM sales_reps WHERE sales_reps.id = ${CUBE}.sales_rep_id)`,
      type: `string`
    }
  },
  
  measures: {
    totalRevenue: {
      sql: `total_amount`,
      type: `sum`,
      format: `currency`
    },
    
    totalTransactions: {
      type: `count`
    },
    
    totalQuantity: {
      sql: `quantity`,
      type: `sum`
    },
    
    averageTransactionValue: {
      sql: `total_amount`,
      type: `avg`,
      format: `currency`
    },
    
    totalDiscountAmount: {
      sql: `(unit_price * quantity * discount_percent / 100)`,
      type: `sum`,
      format: `currency`
    },
    
    grossRevenue: {
      sql: `(unit_price * quantity)`,
      type: `sum`,
      format: `currency`
    },
    
    uniqueCustomers: {
      sql: `customer_id`,
      type: `countDistinct`
    }
  },
  
  preAggregations: {
    // Main pre-aggregation for faster queries
    main: {
      measures: [
        totalRevenue,
        totalTransactions,
        totalQuantity,
        averageTransactionValue,
        uniqueCustomers
      ],
      dimensions: [
        transactionDate,
        channel,
        region,
        productCategory
      ],
      timeDimension: transactionDate,
      granularity: `day`
    }
  }
});