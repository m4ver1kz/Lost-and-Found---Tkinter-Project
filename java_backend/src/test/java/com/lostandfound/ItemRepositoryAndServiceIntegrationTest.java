package com.lostandfound;

import com.lostandfound.dto.DashboardStatsDTO;
import com.lostandfound.dto.ItemRequestDTO;
import com.lostandfound.exception.InvalidStatusTransitionException;
import com.lostandfound.exception.ResourceNotFoundException;
import com.lostandfound.model.Item;
import com.lostandfound.service.ItemService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import java.time.LocalDate;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class ItemRepositoryAndServiceIntegrationTest {

    @Autowired
    private ItemService itemService;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @BeforeEach
    @AfterEach
    void cleanUpDatabase() {
        jdbcTemplate.update("DELETE FROM items");
    }

    @Test
    @DisplayName("Test full CRUD and business workflow against actual MySQL database via JDBC")
    void testFullItemWorkflow() {
        // 1. Add a new item (Report found item)
        ItemRequestDTO request = new ItemRequestDTO(
                "Blue Backpack",
                "Personal Accessories",
                "Navy blue canvas backpack found on bench",
                "Library 2nd Floor",
                LocalDate.now(),
                "9876543210",
                "LOST"
        );

        Item savedItem = itemService.addItem(request);

        assertNotNull(savedItem.getItemId(), "Generated item_id must not be null");
        assertTrue(savedItem.getItemId() > 0, "Generated item_id must be greater than 0");
        assertEquals("Blue Backpack", savedItem.getItemName());
        assertEquals("LOST", savedItem.getStatus(), "Default or initial status must be LOST");

        // 2. Retrieve all items
        List<Item> allItems = itemService.getItems(null, null, null);
        assertEquals(1, allItems.size());
        assertEquals("Blue Backpack", allItems.get(0).getItemName());

        // 3. Retrieve item by ID
        Item retrieved = itemService.getItemById(savedItem.getItemId());
        assertNotNull(retrieved);
        assertEquals(savedItem.getItemId(), retrieved.getItemId());

        // 4. Search items by name
        List<Item> searchMatches = itemService.getItems("backpack", null, null);
        assertEquals(1, searchMatches.size());

        List<Item> noMatches = itemService.getItems("wallet", null, null);
        assertEquals(0, noMatches.size());

        // 5. Filter items by category
        List<Item> categoryMatches = itemService.getItems(null, "Personal Accessories", null);
        assertEquals(1, categoryMatches.size());

        List<Item> wrongCategory = itemService.getItems(null, "Electronics", null);
        assertEquals(0, wrongCategory.size());

        // 6. Filter items by status
        List<Item> lostItems = itemService.getItems(null, null, "LOST");
        assertEquals(1, lostItems.size());

        List<Item> foundItems = itemService.getItems(null, null, "FOUND");
        assertEquals(0, foundItems.size());

        // 7. Verify dashboard statistics before return
        DashboardStatsDTO initialStats = itemService.getDashboardStats();
        assertEquals(1, initialStats.getTotalItems());
        assertEquals(1, initialStats.getLostCount());
        assertEquals(0, initialStats.getFoundCount());

        // 8. Update status to FOUND
        Item updated = itemService.updateItemStatus(savedItem.getItemId(), "FOUND");
        assertEquals("FOUND", updated.getStatus());

        // Verify status in MySQL directly
        String statusInDb = jdbcTemplate.queryForObject(
                "SELECT status FROM items WHERE item_id = ?",
                String.class,
                savedItem.getItemId()
        );
        assertEquals("FOUND", statusInDb);

        // 9. Verify dashboard statistics after return
        DashboardStatsDTO updatedStats = itemService.getDashboardStats();
        assertEquals(1, updatedStats.getTotalItems());
        assertEquals(0, updatedStats.getLostCount());
        assertEquals(1, updatedStats.getFoundCount());

        // 10. Enforce rule: FOUND item can NEVER be reverted back to LOST
        assertThrows(InvalidStatusTransitionException.class, () -> {
            itemService.updateItemStatus(savedItem.getItemId(), "LOST");
        }, "Should throw InvalidStatusTransitionException when trying to revert FOUND item to LOST");

        // 11. Verify non-existent ID throws ResourceNotFoundException
        assertThrows(ResourceNotFoundException.class, () -> {
            itemService.getItemById(999999);
        });
    }
}
