package com.lostandfound.repository;

import com.lostandfound.model.Item;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Repository interface for database operations on items using JDBC.
 */
public interface ItemRepository {

    /**
     * Inserts a new item into MySQL using a parameterized query and returns the item with generated item_id.
     */
    Item save(Item item);

    /**
     * Retrieves all items ordered by date_found descending.
     */
    List<Item> findAll();

    /**
     * Retrieves an item by its unique database ID.
     */
    Optional<Item> findById(int itemId);

    /**
     * Searches items by name using parameterized case-insensitive pattern matching.
     */
    List<Item> searchByName(String itemName);

    /**
     * Filters items by category.
     */
    List<Item> filterByCategory(String category);

    /**
     * Filters items by status ('LOST' or 'FOUND').
     */
    List<Item> filterByStatus(String status);

    /**
     * Dynamically combines search by name, filter by category, and filter by status using parameterized queries.
     */
    List<Item> findBySearchAndFilters(String search, String category, String status);

    /**
     * Updates an item's status in the database.
     * @return true if at least one row was modified, false otherwise.
     */
    boolean updateStatus(int itemId, String status);

    /**
     * Returns item counts grouped by status.
     */
    Map<String, Long> countByStatus();

    /**
     * Returns total item count.
     */
    long countTotal();

    /**
     * Returns item counts grouped by category.
     */
    Map<String, Long> countByCategory();
}
