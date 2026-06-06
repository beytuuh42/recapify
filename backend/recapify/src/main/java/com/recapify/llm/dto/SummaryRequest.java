package com.recapify.llm.dto;

public record SummaryRequest(String title, String media_type, Integer season, Integer episode, String language) {
}
