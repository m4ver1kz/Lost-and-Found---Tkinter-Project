package com.lostandfound;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lostandfound.dto.ItemRequestDTO;
import com.lostandfound.dto.StatusUpdateRequestDTO;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class ItemControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @BeforeEach
    @AfterEach
    void cleanDatabase() {
        jdbcTemplate.update("DELETE FROM items");
    }

    @Test
    @DisplayName("Health endpoint confirms active MySQL database connectivity")
    void testHealthEndpoint() throws Exception {
        mockMvc.perform(get("/api/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(jsonPath("$.database").value("CONNECTED"))
                .andExpect(jsonPath("$.catalog").value("lost_and_found"));
    }

    @Test
    @DisplayName("Complete REST API item lifecycle via HTTP JSON endpoints")
    void testItemRestApiEndpoints() throws Exception {
        // 1. POST /api/items - Create a new item
        ItemRequestDTO request = new ItemRequestDTO(
                "Silver Watch",
                "Personal Accessories",
                "Analog metallic watch",
                "Cafeteria",
                LocalDate.now(),
                "555-1234",
                "LOST"
        );

        String responseBody = mockMvc.perform(post("/api/items")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.itemId").isNumber())
                .andExpect(jsonPath("$.itemName").value("Silver Watch"))
                .andExpect(jsonPath("$.status").value("LOST"))
                .andReturn().getResponse().getContentAsString();

        int createdId = objectMapper.readTree(responseBody).get("itemId").asInt();

        // 2. GET /api/items - List all items
        mockMvc.perform(get("/api/items"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].itemId").value(createdId));

        // 3. GET /api/items/{id} - Get single item
        mockMvc.perform(get("/api/items/" + createdId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.itemName").value("Silver Watch"));

        // 4. PUT /api/items/{id}/status - Mark as FOUND
        StatusUpdateRequestDTO statusUpdate = new StatusUpdateRequestDTO("FOUND");
        mockMvc.perform(put("/api/items/" + createdId + "/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(statusUpdate)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("FOUND"));

        // 5. PUT /api/items/{id}/status - Disallow reverting FOUND to LOST (400 Bad Request)
        StatusUpdateRequestDTO invalidRevert = new StatusUpdateRequestDTO("LOST");
        mockMvc.perform(put("/api/items/" + createdId + "/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRevert)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Invalid Status Transition"));

        // 6. GET /api/dashboard/stats - Verify statistics
        mockMvc.perform(get("/api/dashboard/stats"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalItems").value(1))
                .andExpect(jsonPath("$.lostCount").value(0))
                .andExpect(jsonPath("$.foundCount").value(1));
    }
}
