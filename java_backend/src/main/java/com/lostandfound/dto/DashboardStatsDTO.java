package com.lostandfound.dto;

import java.util.Map;

/**
 * Data Transfer Object containing system statistics for the dashboard.
 */
public class DashboardStatsDTO {

    private long totalItems;
    private long lostCount;
    private long foundCount;
    private Map<String, Long> categoryCounts;

    public DashboardStatsDTO() {
    }

    public DashboardStatsDTO(long totalItems, long lostCount, long foundCount, Map<String, Long> categoryCounts) {
        this.totalItems = totalItems;
        this.lostCount = lostCount;
        this.foundCount = foundCount;
        this.categoryCounts = categoryCounts;
    }

    public long getTotalItems() {
        return totalItems;
    }

    public void setTotalItems(long totalItems) {
        this.totalItems = totalItems;
    }

    public long getLostCount() {
        return lostCount;
    }

    public void setLostCount(long lostCount) {
        this.lostCount = lostCount;
    }

    public long getFoundCount() {
        return foundCount;
    }

    public void setFoundCount(long foundCount) {
        this.foundCount = foundCount;
    }

    public Map<String, Long> getCategoryCounts() {
        return categoryCounts;
    }

    public void setCategoryCounts(Map<String, Long> categoryCounts) {
        this.categoryCounts = categoryCounts;
    }
}
