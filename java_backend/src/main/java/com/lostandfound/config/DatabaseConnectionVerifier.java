package com.lostandfound.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.DatabaseMetaData;

/**
 * Startup component that verifies live connectivity to MySQL via JDBC.
 * Fails clearly if the database connection cannot be established.
 */
@Component
public class DatabaseConnectionVerifier implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DatabaseConnectionVerifier.class);

    private final DataSource dataSource;
    private final JdbcTemplate jdbcTemplate;

    public DatabaseConnectionVerifier(DataSource dataSource, JdbcTemplate jdbcTemplate) {
        this.dataSource = dataSource;
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public void run(String... args) throws Exception {
        log.info("===============================================================");
        log.info("Verifying MySQL database connection via JDBC...");

        try (Connection connection = dataSource.getConnection()) {
            DatabaseMetaData metaData = connection.getMetaData();
            log.info("Successfully connected to MySQL database!");
            log.info("Database Product : {}", metaData.getDatabaseProductName());
            log.info("Database Version : {}", metaData.getDatabaseProductVersion());
            log.info("Catalog / Schema : {}", connection.getCatalog());

            // Verify query execution on the items table
            Integer count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM items", Integer.class);
            log.info("Verified table 'items'. Current recorded rows: {}", count != null ? count : 0);
            log.info("===============================================================");
        } catch (Exception e) {
            log.error("===============================================================");
            log.error("CRITICAL: Failed to connect to MySQL database via JDBC!");
            log.error("Error detail: {}", e.getMessage());
            log.error("Please ensure MySQL is running on the configured host/port,");
            log.error("and that credentials in environment variables or application-local.properties are valid.");
            log.error("===============================================================");
            throw new IllegalStateException("Database connection verification failed: " + e.getMessage(), e);
        }
    }
}
