package com.lostandfound.model;

import java.time.LocalDate;
import java.util.Objects;

/**
 * Domain entity representing an item in the Lost and Found system.
 * Maps directly to the 'items' table in MySQL.
 */
public class Item {

    private Integer itemId;
    private String itemName;
    private String category;
    private String description;
    private String foundLocation;
    private LocalDate dateFound;
    private String contact;
    private String status;

    public Item() {
    }

    public Item(Integer itemId, String itemName, String category, String description,
                String foundLocation, LocalDate dateFound, String contact, String status) {
        this.itemId = itemId;
        this.itemName = itemName;
        this.category = category;
        this.description = description;
        this.foundLocation = foundLocation;
        this.dateFound = dateFound;
        this.contact = contact;
        this.status = status;
    }

    public Integer getItemId() {
        return itemId;
    }

    public void setItemId(Integer itemId) {
        this.itemId = itemId;
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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Item item = (Item) o;
        return Objects.equals(itemId, item.itemId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(itemId);
    }

    @Override
    public String toString() {
        return "Item{" +
                "itemId=" + itemId +
                ", itemName='" + itemName + '\'' +
                ", category='" + category + '\'' +
                ", description='" + description + '\'' +
                ", foundLocation='" + foundLocation + '\'' +
                ", dateFound=" + dateFound +
                ", contact='" + contact + '\'' +
                ", status='" + status + '\'' +
                '}';
    }
}
