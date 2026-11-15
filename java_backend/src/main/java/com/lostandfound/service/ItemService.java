package com.lostandfound.service;

import com.lostandfound.dto.DashboardStatsDTO;
import com.lostandfound.dto.ItemRequestDTO;
import com.lostandfound.exception.InvalidStatusTransitionException;
import com.lostandfound.exception.ResourceNotFoundException;
import com.lostandfound.model.Item;
import com.lostandfound.repository.ItemRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * Service layer implementing business rules and validations for items.
 */
@Service
public class ItemService {

    private static final Logger log = LoggerFactory.getLogger(ItemService.class);

    private final ItemRepository itemRepository;

    public ItemService(ItemRepository itemRepository) {
        this.itemRepository = itemRepository;
    }

    /**
     * Reports a newly found item. Default status is always LOST unless explicitly set.
     */
    @Transactional
    public Item addItem(ItemRequestDTO request) {
        validateItemRequest(request);

        Item item = new Item();
        item.setItemName(request.getItemName().trim());
        item.setCategory(request.getCategory().trim());
        item.setDescription(request.getDescription() != null ? request.getDescription().trim() : null);
        item.setFoundLocation(request.getFoundLocation().trim());
        item.setDateFound(request.getDateFound());
        item.setContact(request.getContact().trim());
        item.setStatus("LOST"); // Rule: initial status is always LOST upon reporting

        Item saved = itemRepository.save(item);
        if (saved.getItemId() == null || saved.getItemId() <= 0) {
            throw new IllegalStateException("Failed to retrieve database-generated item ID after insertion.");
        }

        log.info("Successfully registered item with ID: {}, Name: {}, Status: {}",
                saved.getItemId(), saved.getItemName(), saved.getStatus());
        return saved;
    }

    /**
     * Retrieves all items or filters by search name, category, and status.
     */
    public List<Item> getItems(String search, String category, String status) {
        return itemRepository.findBySearchAndFilters(search, category, status);
    }

    /**
     * Searches items by name.
     */
    public List<Item> searchByName(String name) {
        if (name == null || name.trim().isEmpty()) {
            return itemRepository.findAll();
        }
        return itemRepository.searchByName(name.trim());
    }

    /**
     * Retrieves a single item by its database ID.
     */
    public Item getItemById(int itemId) {
        return itemRepository.findById(itemId)
                .orElseThrow(() -> new ResourceNotFoundException("Item with ID " + itemId + " not found."));
    }

    /**
     * Updates an item's status.
     * Enforces the rule: An item marked as FOUND can NEVER be transitioned back to LOST.
     */
    @Transactional
    public Item updateItemStatus(int itemId, String newStatus) {
        if (newStatus == null || newStatus.isBlank()) {
            throw new IllegalArgumentException("Status cannot be empty.");
        }

        String normalizedStatus = newStatus.trim().toUpperCase();
        if (!normalizedStatus.equals("LOST") && !normalizedStatus.equals("FOUND")) {
            throw new IllegalArgumentException("Invalid status: " + newStatus + ". Status must be 'LOST' or 'FOUND'.");
        }

        Item existing = getItemById(itemId);

        // Core business rule: FOUND items cannot be reverted to LOST
        if ("FOUND".equalsIgnoreCase(existing.getStatus()) && "LOST".equalsIgnoreCase(normalizedStatus)) {
            throw new InvalidStatusTransitionException(
                    "Item with ID " + itemId + " is already marked as FOUND. It cannot be reverted to LOST."
            );
        }

        if (existing.getStatus().equalsIgnoreCase(normalizedStatus)) {
            return existing; // Already in target status
        }

        boolean updated = itemRepository.updateStatus(itemId, normalizedStatus);
        if (!updated) {
            throw new IllegalStateException("Failed to update status for item ID " + itemId + " in MySQL.");
        }

        existing.setStatus(normalizedStatus);
        log.info("Item ID {} status updated to {}", itemId, normalizedStatus);
        return existing;
    }

    /**
     * Compiles dashboard statistics.
     */
    public DashboardStatsDTO getDashboardStats() {
        long total = itemRepository.countTotal();
        Map<String, Long> statusCounts = itemRepository.countByStatus();
        Map<String, Long> categoryCounts = itemRepository.countByCategory();

        long lostCount = statusCounts.getOrDefault("LOST", 0L);
        long foundCount = statusCounts.getOrDefault("FOUND", 0L);

        return new DashboardStatsDTO(total, lostCount, foundCount, categoryCounts);
    }

    private void validateItemRequest(ItemRequestDTO request) {
        if (request.getItemName() == null || request.getItemName().isBlank()) {
            throw new IllegalArgumentException("Item name cannot be blank.");
        }
        if (request.getCategory() == null || request.getCategory().isBlank()) {
            throw new IllegalArgumentException("Category cannot be blank.");
        }
        if (request.getFoundLocation() == null || request.getFoundLocation().isBlank()) {
            throw new IllegalArgumentException("Found location cannot be blank.");
        }
        if (request.getDateFound() == null) {
            throw new IllegalArgumentException("Date found is required.");
        }
        if (request.getDateFound().isAfter(LocalDate.now())) {
            throw new IllegalArgumentException("Date found cannot be in the future.");
        }
        if (request.getContact() == null || request.getContact().isBlank()) {
            throw new IllegalArgumentException("Contact cannot be blank.");
        }
        if (request.getStatus() != null && !request.getStatus().isBlank()) {
            String st = request.getStatus().trim().toUpperCase();
            if (!st.equals("LOST") && !st.equals("FOUND")) {
                throw new IllegalArgumentException("Status must be either 'LOST' or 'FOUND'.");
            }
        }
    }
}
