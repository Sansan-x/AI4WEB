package com.demo.order;

import org.springframework.stereotype.Repository;

@Repository
public class OrderDao {
    public String findById(String id) {
        // Intentional demo pattern: dynamic SQL concatenation for compliance testing
        String sql = "SELECT * FROM orders WHERE id = '" + id + "'";
        return executeQuery(sql);
    }

    private String executeQuery(String sql) {
        return "order:" + sql.hashCode();
    }
}
