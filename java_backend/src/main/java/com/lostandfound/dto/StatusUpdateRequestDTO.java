package com.lostandfound.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

/**
 * Request payload for updating the status of an item.
 */
public class StatusUpdateRequestDTO {

    @NotBlank(message = "Status is required.")
    @Pattern(regexp = "^(LOST|FOUND)$", message = "Status must be either 'LOST' or 'FOUND'.")
    private String status;

    public StatusUpdateRequestDTO() {
    }

    public StatusUpdateRequestDTO(String status) {
        this.status = status;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
