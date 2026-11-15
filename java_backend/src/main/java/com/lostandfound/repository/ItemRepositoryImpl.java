package com.lostandfound.repository;

import com.lostandfound.model.Item;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * JDBC implementation of ItemRepository utilizing Spring JdbcTemplate and parameterized queries.
 */
@Repository
public class ItemRepositoryImpl implements ItemRepository {

    private final JdbcTemplate jdbcTemplate;

    public ItemRepositoryImpl(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    private final RowMapper<Item> itemRowMapper = (rs, rowNum) -> new Item(
            rs.getInt("item_id"),
            rs.getString("item_name"),
            rs.getString("category"),
            rs.getString("description"),
            rs.getString("found_location"),
            rs.getDate("date_found") != null ? rs.getDate("date_found").toLocalDate() : null,
            rs.getString("contact"),
            rs.getString("status")
    );

    @Override
    public Item save(Item item) {
        String sql = "INSERT INTO items (item_name, category, description, found_location, date_found, contact, status) " +
                     "VALUES (?, ?, ?, ?, ?, ?, ?)";

        KeyHolder keyHolder = new GeneratedKeyHolder();

        int rowsAffected = jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, item.getItemName());
            ps.setString(2, item.getCategory());
            ps.setString(3, item.getDescription());
            ps.setString(4, item.getFoundLocation());
            ps.setDate(5, item.getDateFound() != null ? Date.valueOf(item.getDateFound()) : null);
            ps.setString(6, item.getContact());
            ps.setString(7, item.getStatus() != null ? item.getStatus() : "LOST");
            return ps;
        }, keyHolder);

        if (rowsAffected > 0 && keyHolder.getKey() != null) {
            item.setItemId(keyHolder.getKey().intValue());
        }

        return item;
    }

    @Override
    public List<Item> findAll() {
        String sql = "SELECT item_id, item_name, category, description, found_location, date_found, contact, status " +
                     "FROM items ORDER BY date_found DESC, item_id DESC";
        return jdbcTemplate.query(sql, itemRowMapper);
    }

    @Override
    public Optional<Item> findById(int itemId) {
        String sql = "SELECT item_id, item_name, category, description, found_location, date_found, contact, status " +
                     "FROM items WHERE item_id = ?";
        try {
            Item item = jdbcTemplate.queryForObject(sql, itemRowMapper, itemId);
            return Optional.ofNullable(item);
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    @Override
    public List<Item> searchByName(String itemName) {
        String sql = "SELECT item_id, item_name, category, description, found_location, date_found, contact, status " +
                     "FROM items WHERE LOWER(item_name) LIKE LOWER(?) ORDER BY date_found DESC";
        String pattern = "%" + (itemName != null ? itemName.trim() : "") + "%";
        return jdbcTemplate.query(sql, itemRowMapper, pattern);
    }

    @Override
    public List<Item> filterByCategory(String category) {
        String sql = "SELECT item_id, item_name, category, description, found_location, date_found, contact, status " +
                     "FROM items WHERE category = ? ORDER BY date_found DESC";
        return jdbcTemplate.query(sql, itemRowMapper, category);
    }

    @Override
    public List<Item> filterByStatus(String status) {
        String sql = "SELECT item_id, item_name, category, description, found_location, date_found, contact, status " +
                     "FROM items WHERE status = ? ORDER BY date_found DESC";
        return jdbcTemplate.query(sql, itemRowMapper, status);
    }

    @Override
    public List<Item> findBySearchAndFilters(String search, String category, String status) {
        StringBuilder sql = new StringBuilder(
                "SELECT item_id, item_name, category, description, found_location, date_found, contact, status FROM items WHERE 1=1"
        );
        List<Object> params = new ArrayList<>();

        if (search != null && !search.trim().isEmpty()) {
            sql.append(" AND LOWER(item_name) LIKE LOWER(?)");
            params.add("%" + search.trim() + "%");
        }

        if (category != null && !category.trim().isEmpty() && !category.equalsIgnoreCase("ALL")) {
            sql.append(" AND category = ?");
            params.add(category.trim());
        }

        if (status != null && !status.trim().isEmpty() && !status.equalsIgnoreCase("ALL")) {
            sql.append(" AND status = ?");
            params.add(status.trim().toUpperCase());
        }

        sql.append(" ORDER BY date_found DESC, item_id DESC");

        return jdbcTemplate.query(sql.toString(), itemRowMapper, params.toArray());
    }

    @Override
    public boolean updateStatus(int itemId, String status) {
        String sql = "UPDATE items SET status = ? WHERE item_id = ?";
        int updated = jdbcTemplate.update(sql, status, itemId);
        return updated > 0;
    }

    @Override
    public Map<String, Long> countByStatus() {
        String sql = "SELECT status, COUNT(*) AS cnt FROM items GROUP BY status";
        Map<String, Long> counts = new HashMap<>();
        counts.put("LOST", 0L);
        counts.put("FOUND", 0L);

        jdbcTemplate.query(sql, rs -> {
            String st = rs.getString("status");
            long cnt = rs.getLong("cnt");
            counts.put(st, cnt);
        });

        return counts;
    }

    @Override
    public long countTotal() {
        String sql = "SELECT COUNT(*) FROM items";
        Long count = jdbcTemplate.queryForObject(sql, Long.class);
        return count != null ? count : 0L;
    }

    @Override
    public Map<String, Long> countByCategory() {
        String sql = "SELECT category, COUNT(*) AS cnt FROM items GROUP BY category ORDER BY cnt DESC";
        Map<String, Long> counts = new HashMap<>();

        jdbcTemplate.query(sql, rs -> {
            String cat = rs.getString("category");
            long cnt = rs.getLong("cnt");
            counts.put(cat, cnt);
        });

        return counts;
    }
}
