package com.lostandfound.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PastOrPresent;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.time.LocalDate;

/**
 * Data Transfer Object for creating or reporting a found item.
 */
public class ItemRequestDTO {

    @NotBlank(message = "Item name is required and cannot be empty.")
    @Size(max = 100, message = "Item name must not exceed 100 characters.")
    private String itemName;

    @NotBlank(message = "Category is required and cannot be empty.")
    @Size(max = 50, message = "Category must not exceed 50 characters.")
    private String category;

    @Size(max = 255, message = "Description must not exceed 255 characters.")
    private String description;

    @NotBlank(message = "Found location is required and cannot be empty.")
    @Size(max = 100, message = "Found location must not exceed 100 characters.")
    private String foundLocation;

    @NotNull(message = "Date found is required.")
    @PastOrPresent(message = "Date found cannot be in the future.")
    private LocalDate dateFound;

    @NotBlank(message = "Contact information is required.")
    @Size(max = 20, message = "Contact must not exceed 20 characters.")
    private String contact;

    @Pattern(regexp = "^(LOST|FOUND)$", message = "Status must be either 'LOST' or 'FOUND'.")
    private String status = "LOST";

    public ItemRequestDTO() {
    }

    public ItemRequestDTO(String itemName, String category, String description,
                          String foundLocation, LocalDate dateFound, String contact, String status) {
        this.itemName = itemName;
        this.category = category;
        this.description = description;
        this.foundLocation = foundLocation;
        this.dateFound = dateFound;
        this.contact = contact;
        this.status = (status != null && !status.isBlank()) ? status : "LOST";
    }

    public String getItemName() {
        return itemName;
    }

    public void setItemName(String itemName) {
        this.itemName = itemName;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getFoundLocation() {
        return foundLocation;
    }

    public void setFoundLocation(String foundLocation) {
        this.foundLocation = foundLocation;
    }

    public LocalDate getDateFound() {
        return dateFound;
    }

    public void setDateFound(LocalDate dateFound) {
        this.dateFound = dateFound;
    }

    public String getContact() {
        return contact;
    }

    public void setContact(String contact) {
        this.contact = contact;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
