package com.lostandfound.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Health check endpoint verifying Java backend status and MySQL JDBC connectivity.
 * Endpoint: GET /api/health
 */
@RestController
@RequestMapping("/api/health")
@CrossOrigin(origins = "*")
public class HealthController {

    private final JdbcTemplate jdbcTemplate;
    private final DataSource dataSource;

    public HealthController(JdbcTemplate jdbcTemplate, DataSource dataSource) {
        this.jdbcTemplate = jdbcTemplate;
        this.dataSource = dataSource;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> checkHealth() {
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("timestamp", LocalDateTime.now());
        response.put("backend", "RUNNING");

        try (Connection conn = dataSource.getConnection()) {
            Integer result = jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            if (result != null && result == 1) {
                DatabaseMetaData meta = conn.getMetaData();
                response.put("status", "UP");
                response.put("database", "CONNECTED");
                response.put("databaseProduct", meta.getDatabaseProductName());
                response.put("databaseVersion", meta.getDatabaseProductVersion());
                response.put("catalog", conn.getCatalog());
                return ResponseEntity.ok(response);
            } else {
                response.put("status", "DOWN");
                response.put("database", "UNEXPECTED_RESPONSE");
                return new ResponseEntity<>(response, HttpStatus.SERVICE_UNAVAILABLE);
            }
        } catch (Exception ex) {
            response.put("status", "DOWN");
            response.put("database", "DISCONNECTED");
            response.put("error", "Unable to establish JDBC connection to MySQL");
            return new ResponseEntity<>(response, HttpStatus.SERVICE_UNAVAILABLE);
        }
    }
}
