package com.lostandfound.controller;

import com.lostandfound.dto.DashboardStatsDTO;
import com.lostandfound.dto.ItemRequestDTO;
import com.lostandfound.dto.StatusUpdateRequestDTO;
import com.lostandfound.model.Item;
import com.lostandfound.service.ItemService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * REST controller exposing endpoints for lost and found items.
 */
@RestController
@RequestMapping("/api/items")
@CrossOrigin(origins = "*")
public class ItemController {

    private final ItemService itemService;

    public ItemController(ItemService itemService) {
        this.itemService = itemService;
    }

    /**
     * Endpoint 2: POST /api/items
     * Report a newly found item.
     * Inserts into MySQL with generated item_id and initial status set to LOST.
     */
    @PostMapping
    public ResponseEntity<Item> addItem(@Valid @RequestBody ItemRequestDTO request) {
        Item created = itemService.addItem(request);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    /**
     * Endpoint 3, 6, 7: GET /api/items
     * Retrieves all items from MySQL with optional filtering by category or status.
     * Examples:
     * - GET /api/items
     * - GET /api/items?category={category}
     * - GET /api/items?status={status}
     */
    @GetMapping
    public ResponseEntity<List<Item>> getItems(
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String status) {
        List<Item> items = itemService.getItems(search, category, status);
        return ResponseEntity.ok(items);
    }

    /**
     * Endpoint 5: GET /api/items/search?name={name}
     * Search items by name.
     */
    @GetMapping("/search")
    public ResponseEntity<List<Item>> searchItemsByName(@RequestParam(name = "name", required = false) String name) {
        List<Item> items = itemService.searchByName(name);
        return ResponseEntity.ok(items);
    }

    /**
     * Endpoint 4: GET /api/items/{id}
     * Retrieve one item using its database ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<Item> getItemById(@PathVariable int id) {
        Item item = itemService.getItemById(id);
        return ResponseEntity.ok(item);
    }

    /**
     * Endpoint 8: PATCH /api/items/{id}/status (and PUT)
     * Update the status of an item (e.g. from LOST to FOUND).
     * Prevents reverting an already FOUND item back to LOST.
     */
    @PatchMapping("/{id}/status")
    public ResponseEntity<Item> patchStatus(
            @PathVariable int id,
            @Valid @RequestBody StatusUpdateRequestDTO request) {
        Item updated = itemService.updateItemStatus(id, request.getStatus());
        return ResponseEntity.ok(updated);
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<Item> putStatus(
            @PathVariable int id,
            @Valid @RequestBody StatusUpdateRequestDTO request) {
        Item updated = itemService.updateItemStatus(id, request.getStatus());
        return ResponseEntity.ok(updated);
    }

    /**
     * Endpoint 9: GET /api/items/stats
     * Return item counts and dashboard summary statistics.
     */
    @GetMapping("/stats")
    public ResponseEntity<DashboardStatsDTO> getStats() {
        DashboardStatsDTO stats = itemService.getDashboardStats();
        return ResponseEntity.ok(stats);
    }
}
